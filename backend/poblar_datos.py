import random
import time
from owlready2 import *
from SPARQLWrapper import SPARQLWrapper, JSON
from faker import Faker

CANTIDAD_LIBROS_DBPEDIA = 200  
CANTIDAD_ESTUDIANTES = 100
CANTIDAD_DOCENTES = 50
CANTIDAD_BIBLIOTECARIOS = 20
PROBABILIDAD_PRESTAMO = 0.7    

ONTO_FILE = "biblioteca.owl"
IRI_BASE = "http://uni.edu/biblioteca.owl#"

fake = Faker('es_ES')

print(f"--- Cargando estructura base: {ONTO_FILE} ---")
onto = get_ontology(ONTO_FILE).load()

def limpiar_texto(texto):
    if not texto: return "Desconocido"
    texto = texto.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    texto = texto.replace("ñ", "n").replace("Ñ", "N")
    return "".join(x for x in texto if x.isalnum())

def obtener_libros_masivos(limite):
    print(f">>> Conectando a DBpedia para descargar {limite} libros...")
    sparql = SPARQLWrapper("http://es.dbpedia.org/sparql")
    
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
    libros = []
    for _ in range(cantidad_faltante):
        libros.append({
            "titulo": fake.catch_phrase().title(),
            "autor": fake.name(),
            "editorial": fake.company(),
            "pais": fake.country()
        })
    return libros

def crear_datos_demo_garantizados():
    """
    Crea manualmente los datos para probar Quechua, Alemán y Francés.
    """
    print(">>> Creando datos DEMO multilingües (Arguedas, Kafka, etc)...")
    
    # Referencias directas a clases
    Libro = onto.Libro
    Persona = onto.Persona
    Editorial = onto.Editorial
    
    # 1. José María Arguedas (Quechua)
    aut_arguedas = Persona("autor_arguedas")
    aut_arguedas.nombre = ["José María Arguedas"]
    
    l_yawar = Libro("libro_yawar_fiesta")
    l_yawar.titulo = ["Yawar Fiesta"]
    l_yawar.anio_publicacion = [1941]
    l_yawar.pais_origen = ["Perú"]
    
    aut_arguedas.escribe.append(l_yawar) 

    # 2. Franz Kafka (Alemán)
    aut_kafka = Persona("autor_kafka")
    aut_kafka.nombre = ["Franz Kafka"]
    
    l_meta = Libro("libro_metamorfosis")
    l_meta.titulo = ["Die Verwandlung"]
    l_meta.anio_publicacion = [1915]
    
    aut_kafka.escribe.append(l_meta)

    return [l_yawar, l_meta] 

def ejecutar_poblado():
    start_time = time.time()
    libros_creados = []
    
    with onto:
        libros_creados.extend(crear_datos_demo_garantizados())

        # 2. Insertar Datos Masivos (DBpedia)
        datos_libros = obtener_libros_masivos(CANTIDAD_LIBROS_DBPEDIA)
        
        if len(datos_libros) < CANTIDAD_LIBROS_DBPEDIA:
            faltan = CANTIDAD_LIBROS_DBPEDIA - len(datos_libros)
            print(f">>> Rellenando {faltan} libros con datos sintéticos...")
            datos_libros += generar_libros_sinteticos(faltan)
            
        print(f">>> Procesando {len(datos_libros)} libros masivos...")
        
        for i, item in enumerate(datos_libros):
            hash_id = str(random.randint(1000, 9999))
            # IDs seguros
            id_libro = limpiar_texto(item["titulo"])[:30] + hash_id
            id_autor = "aut_" + limpiar_texto(item["autor"])[:20] + hash_id
            id_editorial = "edit_" + limpiar_texto(item["editorial"])[:20] + hash_id
            
            # Editorial
            if onto[id_editorial]:
                editorial = onto[id_editorial]
            else:
                editorial = onto.Editorial(id_editorial)
                editorial.nombre = [item["editorial"]]
                editorial.pais_origen = [item["pais"]]
            
            # Autor
            if onto[id_autor]:
                autor = onto[id_autor]
            else:
                autor = onto.Persona(id_autor)
                autor.nombre = [item["autor"]]
            
            # Libro
            libro = onto.Libro(id_libro)
            libro.titulo = [item["titulo"]]
            libro.anio_publicacion = [random.randint(1950, 2023)]
            libro.estado_libro = ["Disponible"]
            
            autor.escribe.append(libro)
            
            editorial.publica.append(libro)
            
            libros_creados.append(libro)
            
            if i % 50 == 0 and i > 0:
                print(f"   ... creados {i} libros")

        # 3. ESTUDIANTES
        print(f">>> Generando {CANTIDAD_ESTUDIANTES} estudiantes...")
        carreras = ["Sistemas", "Derecho", "Medicina", "Arquitectura", "Psicologia", "Civil"]
        
        for i in range(CANTIDAD_ESTUDIANTES):
            est = onto.Estudiante(f"Estudiante_{i+1}")
            est.nombre = [fake.name()]
            est.codigo_sis = [str(random.randint(20200000, 20250000))]
            est.carrera = [random.choice(carreras)]
            
            # Préstamos aleatorios
            if libros_creados and random.random() < PROBABILIDAD_PRESTAMO:
                libro_prestado = random.choice(libros_creados)
                # Estudiante -> toma_prestado -> Libro
                est.toma_prestado.append(libro_prestado)
                libro_prestado.estado_libro = ["Prestado"]

        # 4. DOCENTES Y BIBLIOTECARIOS
        print(f">>> Generando personal ({CANTIDAD_DOCENTES} docentes, {CANTIDAD_BIBLIOTECARIOS} bibliotecarios)...")
        
        for i in range(CANTIDAD_DOCENTES):
            doc = onto.Docente(f"Docente_{i+1}")
            doc.nombre = [fake.name()]
            doc.departamento = [random.choice(["Exactas", "Humanidades", "Salud", "Tecnología"])]
            doc.item_docente = [str(random.randint(1000, 5000))]

        for i in range(CANTIDAD_BIBLIOTECARIOS):
            bib = onto.Bibliotecario(f"Bibliotecario_{i+1}")
            bib.nombre = [fake.name()]
            bib.turno = [random.choice(["Mañana", "Tarde", "Noche"])]
            bib.id_empleado = [f"BIB-{random.randint(100, 999)}"]

    print(">>> Guardando ontología...")
    onto.save(file=ONTO_FILE)
    
    print(f"--- ¡LISTO! Ontología guardada en {ONTO_FILE} ---")
    print(f"Total individuos: {len(list(onto.individuals()))}")

if __name__ == "__main__":
    ejecutar_poblado()