import random
import time
from owlready2 import *
from SPARQLWrapper import SPARQLWrapper, JSON
from faker import Faker

# --- CONFIGURACIÓN DEL BATCH ---
CANTIDAD_LIBROS_DBPEDIA = 200  # Intentará traer esta cantidad
CANTIDAD_ESTUDIANTES = 100
CANTIDAD_DOCENTES = 50
CANTIDAD_BIBLIOTECARIOS = 20
PROBABILIDAD_PRESTAMO = 0.7    # 70% de los estudiantes tendrán un libro

ONTO_FILE = "biblioteca.owl"
IRI_BASE = "http://uni.edu/biblioteca.owl#"

# Inicializar Faker
fake = Faker('es_ES')

print(f"--- Cargando estructura base: {ONTO_FILE} ---")
onto = get_ontology(ONTO_FILE).load()

def limpiar_texto(texto):
    """Limpia strings para usarlos como IDs seguros (sin tildes ni espacios)"""
    texto = texto.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    texto = texto.replace("ñ", "n").replace("Ñ", "N")
    # Dejar solo alfanuméricos
    return "".join(x for x in texto if x.isalnum())

def obtener_libros_masivos(limite):
    print(f">>> Conectando a DBpedia para descargar {limite} libros...")
    sparql = SPARQLWrapper("http://es.dbpedia.org/sparql")
    
    # Consulta optimizada para traer más datos
    query = f"""
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?titulo ?autor ?editorial ?pais
    WHERE {{
      ?libro a dbo:Book ;
             rdfs:label ?titulo ;
             dbo:author ?aResource .
      
      ?aResource rdfs:label ?autor .
      
      OPTIONAL {{ 
        ?libro dbo:publisher ?eResource . 
        ?eResource rdfs:label ?editorial .
        OPTIONAL {{ ?eResource dbo:location ?pResource . ?pResource rdfs:label ?pais }}
      }}
      
      FILTER (LANG(?titulo) = 'es')
      FILTER (LANG(?autor) = 'es')
    }}
    LIMIT {limite}
    """
    
    try:
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        # Timeout de 30 segs para evitar bloqueos
        sparql.setTimeout(30) 
        results = sparql.query().convert()
        
        datos = []
        for result in results["results"]["bindings"]:
            datos.append({
                "titulo": result["titulo"]["value"],
                "autor": result["autor"]["value"],
                "editorial": result.get("editorial", {}).get("value", "Editorial Generica"),
                "pais": result.get("pais", {}).get("value", "Desconocido")
            })
        return datos
    except Exception as e:
        print(f"!!! Error conectando a DBpedia: {e}")
        print("!!! Se generarán libros sintéticos en su lugar.")
        return []

def generar_libros_sinteticos(cantidad_faltante):
    """Si DBpedia falla o trae pocos, rellenamos con Faker"""
    libros = []
    for _ in range(cantidad_faltante):
        libros.append({
            "titulo": fake.catch_phrase().title(),
            "autor": fake.name(),
            "editorial": fake.company(),
            "pais": fake.country()
        })
    return libros

def ejecutar_poblado():
    start_time = time.time()
    libros_creados = []
    
    with onto:
        # ---------------------------------------------------------
        # 1. LIBROS (DBpedia + Relleno)
        # ---------------------------------------------------------
        datos_libros = obtener_libros_masivos(CANTIDAD_LIBROS_DBPEDIA)
        
        # Si DBpedia trajo menos de lo esperado, rellenar
        if len(datos_libros) < CANTIDAD_LIBROS_DBPEDIA:
            faltan = CANTIDAD_LIBROS_DBPEDIA - len(datos_libros)
            print(f">>> Rellenando {faltan} libros con datos sintéticos...")
            datos_libros += generar_libros_sinteticos(faltan)
            
        print(f">>> Insertando {len(datos_libros)} libros y autores en la ontología...")
        
        for i, item in enumerate(datos_libros):
            # ID único: Título + un número hash corto para evitar colisiones si hay títulos iguales
            hash_id = str(random.randint(1000, 9999))
            id_libro = limpiar_texto(item["titulo"])[:25] + hash_id
            id_autor = limpiar_texto(item["autor"])[:20] + hash_id
            id_editorial = limpiar_texto(item["editorial"])[:20] + hash_id
            
            # Editorial
            if not onto[id_editorial]: # Crear solo si no existe
                editorial = onto.Editorial(id_editorial)
                editorial.nombre = [item["editorial"]]
                editorial.pais_origen = [item["pais"]]
            else:
                editorial = onto[id_editorial]
            
            # Autor
            if not onto[id_autor]:
                autor = onto.Persona(id_autor)
                autor.nombre = [item["autor"]]
            else:
                autor = onto[id_autor]
            
            # Libro
            libro = onto.Libro(id_libro)
            libro.titulo = [item["titulo"]]
            libro.anio_publicacion = [random.randint(1950, 2023)]
            libro.estado_libro = ["Disponible"]
            
            # Relaciones
            libro.escribe.append(autor)
            editorial.publica.append(libro)
            
            libros_creados.append(libro)
            
            if i % 50 == 0 and i > 0:
                print(f"   ... procesados {i} libros")

        # ---------------------------------------------------------
        # 2. USUARIOS (Estudiantes)
        # ---------------------------------------------------------
        print(f">>> Generando {CANTIDAD_ESTUDIANTES} estudiantes...")
        for i in range(CANTIDAD_ESTUDIANTES):
            est_id = f"Estudiante{i+1}"
            est = onto.Estudiante(est_id)
            est.nombre = [fake.name()]
            est.codigo_sis = [str(random.randint(20200000, 20250000))]
            est.carrera = [random.choice(["Sistemas", "Derecho", "Medicina", "Arquitectura", "Psicologia", "Civil"])]
            est.email = [fake.email()]
            est.fecha_registro = [fake.date_between(start_date='-4y', end_date='today')]
            
            # Asignar Préstamos (Relación)
            if libros_creados and random.random() < PROBABILIDAD_PRESTAMO:
                # Un estudiante puede tener 1 o 2 libros
                num_libros = random.choice([1, 2])
                for _ in range(num_libros):
                    libro_prestado = random.choice(libros_creados)
                    est.toma_prestado.append(libro_prestado)
                    libro_prestado.estado_libro = ["Prestado"]

        # ---------------------------------------------------------
        # 3. DOCENTES Y BIBLIOTECARIOS
        # ---------------------------------------------------------
        print(f">>> Generando {CANTIDAD_DOCENTES} docentes y {CANTIDAD_BIBLIOTECARIOS} bibliotecarios...")
        
        for i in range(CANTIDAD_DOCENTES):
            doc = onto.Docente(f"Docente{i+1}")
            doc.nombre = [fake.name()]
            doc.departamento = [random.choice(["Ciencias Exactas", "Humanidades", "Salud", "Tecnología"])]
            doc.item_docente = [str(random.randint(1000, 5000))]

        for i in range(CANTIDAD_BIBLIOTECARIOS):
            bib = onto.Bibliotecario(f"Bibliotecario{i+1}")
            bib.nombre = [fake.name()]
            bib.turno = [random.choice(["Mañana", "Tarde", "Noche"])]
            bib.id_empleado = [f"BIB-{random.randint(100, 999)}"]

    print(">>> Guardando archivo .owl (esto puede tardar un poco)...")
    onto.save(file=ONTO_FILE)
    
    tiempo_total = time.time() - start_time
    print(f"--- ¡PROCESO TERMINADO en {tiempo_total:.2f} segundos! ---")
    print(f"Total aproximado de individuos: {len(list(onto.individuals()))}")

if __name__ == "__main__":
    ejecutar_poblado()