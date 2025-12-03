from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Any
import owlready2
from owlready2 import *
import os
import types
import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from SPARQLWrapper import SPARQLWrapper, JSON

# --- Configuración ---
ONTO_FILE = "biblioteca.owl"
IRI_BASE = "http://uni.edu/biblioteca.owl#"

app = FastAPI(title="API Gestión Biblioteca OWL", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # El asterisco permite conexines desde CUALQUIER lado (React, Postman, Móvil)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

onto = None

# --- Modelos Pydantic (Para recibir datos JSON) ---
class IndividualCreate(BaseModel):
    name: str
    class_name: str

class DataPropertyUpdate(BaseModel):
    individual: str
    property: str
    value: Any # Recibe string, int, etc.

class RelationCreate(BaseModel):
    subject: str
    property: str
    object: str

class SPARQLQuery(BaseModel):
    query: str

# --- Inicialización de la Ontología (T-BOX) ---
def inicializar_ontologia_base():
    global onto
    
    # ---------------------------------------------------------
    # 1. CARGA O CREACIÓN DE LA ONTOLOGÍA (LO QUE FALTABA)
    # ---------------------------------------------------------
    if not os.path.exists(ONTO_FILE):
        print(f"--- Creando ontología desde cero: {ONTO_FILE} ---")
        onto = get_ontology(IRI_BASE)
    else:
        print(f"--- Cargando ontología existente: {ONTO_FILE} ---")
        onto = get_ontology(ONTO_FILE).load()

    # ---------------------------------------------------------
    # 2. DEFINICIÓN DE ESTRUCTURA (Multilingüe y Ordenada)
    # ---------------------------------------------------------
    with onto:
        
        # --- NIVEL 1: CLASES BASE (Padres) ---
        
        class Persona(Thing): 
            label = [locstr("Persona", "es"), locstr("Person", "en")]
            comment = [locstr("Ser humano", "es"), locstr("Human being", "en")]
        
        class Organizacion(Thing): 
            label = [locstr("Organización", "es"), locstr("Organization", "en")]
        
        class Publicacion(Thing): 
            label = [locstr("Publicación", "es"), locstr("Publication", "en")]

        # --- NIVEL 2: SUBCLASES INTERMEDIAS ---
        
        class Usuario(Persona): 
            label = [locstr("Usuario", "es"), locstr("User", "en")]
            
        class Bibliotecario(Persona): 
            label = [locstr("Bibliotecario", "es"), locstr("Librarian", "en")]
            
        class Biblioteca(Organizacion): 
            label = [locstr("Biblioteca", "es"), locstr("Library", "en")]
            
        class Editorial(Organizacion):
            label = [locstr("Editorial", "es"), locstr("Publisher", "en")]
            
        class PublicacionPeriodica(Publicacion):
            label = [locstr("Publicación Periódica", "es"), locstr("Periodical", "en")]

        # --- NIVEL 3: CLASES ESPECÍFICAS (Hojas) ---

        class Docente(Usuario): 
            label = [locstr("Docente", "es"), locstr("Professor", "en")]
        
        class Estudiante(Usuario): 
            label = [locstr("Estudiante", "es"), locstr("Student", "en")]

        class Libro(Publicacion): 
            label = [locstr("Libro", "es"), locstr("Book", "en")]
        
        class Revista(PublicacionPeriodica): 
            label = [locstr("Revista", "es"), locstr("Magazine", "en")]
            
        class Periodico(PublicacionPeriodica):
            label = [locstr("Periódico", "es"), locstr("Newspaper", "en")]

        # --- PROPIEDADES DE DATOS (Atributos) ---
        
        class titulo(DataProperty):
            label = [locstr("título", "es"), locstr("title", "en")]
            range = [str]

        class nombre(DataProperty):
            label = [locstr("nombre", "es"), locstr("name", "en")]
            range = [str]
            
        class anio_publicacion(DataProperty):
            label = [locstr("año publicación", "es"), locstr("year", "en")]
            range = [int]
            
        # Agrega aquí el resto de tus propiedades (ci, codigo_sis, etc.) 
        # Si no las defines, owlready2 las creará dinámicamente, pero mejor definirlas.
        class codigo_sis(DataProperty): domain = [Estudiante]; range = [str]
        class carrera(DataProperty): domain = [Estudiante]; range = [str]
        class item_docente(DataProperty): domain = [Docente]; range = [str]
        class departamento(DataProperty): domain = [Docente]; range = [str]
        class id_empleado(DataProperty): domain = [Bibliotecario]; range = [str]
        class turno(DataProperty): range = [str]
        class isbn(DataProperty): domain = [Libro]; range = [str]
        class estado_libro(DataProperty): range = [str]
        class resumen(DataProperty): range = [str]
        class pais_origen(DataProperty): range = [str]
        class sitio_web(DataProperty): domain = [Editorial]; range = [str]

        # --- PROPIEDADES DE OBJETO (Relaciones) ---

        class escribe(ObjectProperty):
            label = [locstr("escribe", "es"), locstr("writes", "en")]
            domain = [Persona]
            range = [Publicacion]
            
        class publica(ObjectProperty):
            label = [locstr("publica", "es"), locstr("publishes", "en")]
            domain = [Editorial]
            range = [Publicacion]

        class toma_prestado(ObjectProperty):
            label = [locstr("toma prestado", "es"), locstr("borrows", "en")]
            domain = [Usuario]
            range = [Libro]

        class gestiona(ObjectProperty):
            domain = [Bibliotecario]
            range = [Thing]

        class trabaja_en(ObjectProperty):
            domain = [Bibliotecario]
            range = [Biblioteca]

    # Guardar cambios finales
    onto.save(file=ONTO_FILE)
    print("--- Ontología inicializada CORRECTAMENTE (Multilingüe y Estructurada) ---")


    

# --- Utilidades de Búsqueda ---
def get_thing(name: str):
    """Busca clase o individuo por nombre."""
    res = onto[name]
    if not res:
        raise HTTPException(status_code=404, detail=f"Entidad '{name}' no encontrada.")
    return res

# --- Eventos ---
@app.on_event("startup")
def startup_event():
    inicializar_ontologia_base()

# --- ENDPOINTS ---

@app.get("/")
def home():
    return {"mensaje": "API de Ontología de Biblioteca funcionando", "archivo": ONTO_FILE}

# 1. Crear Individuos (A-Box)
@app.post("/individuos/")
def crear_individuo(ind: IndividualCreate):
    clase = onto[ind.class_name]
    if not clase:
        raise HTTPException(404, "Clase no encontrada")
    
    with onto:
        nuevo = clase(ind.name)
    
    onto.save(file=ONTO_FILE)
    return {"mensaje": f"Creado '{ind.name}' de tipo '{ind.class_name}'"}

# 2. Asignar Datos (Data Properties)
@app.post("/individuos/datos")
def agregar_dato(data: DataPropertyUpdate):
    ind = get_thing(data.individual)
    prop = get_thing(data.property)
    
    # Owlready2 maneja las propiedades como listas o valores directos
    # Intentamos asignar. Si es fecha string, owlready intenta parsear, pero mejor enviarlo limpio
    try:
        # Verificamos si la propiedad existe en el individuo, si es lista agregamos
        actual = getattr(ind, data.property)
        if isinstance(actual, list):
            actual.append(data.value)
        else:
            setattr(ind, data.property, data.value)
    except Exception as e:
        raise HTTPException(500, f"Error asignando dato: {str(e)}")

    onto.save(file=ONTO_FILE)
    return {"mensaje": f"Actualizado {data.individual}: {data.property} = {data.value}"}

# 3. Crear Relaciones (Object Properties)
@app.post("/individuos/relacion")
def crear_relacion(rel: RelationCreate):
    sujeto = get_thing(rel.subject)
    objeto = get_thing(rel.object)
    propiedad = get_thing(rel.property)
    
    try:
        actual = getattr(sujeto, rel.property)
        actual.append(objeto)
    except Exception as e:
         # Si no es lista (FunctionalProperty), se asigna directo
        setattr(sujeto, rel.property, objeto)
        
    onto.save(file=ONTO_FILE)
    return {"mensaje": f"Relación creada: {rel.subject} --[{rel.property}]--> {rel.object}"}

# 4. Consultar Individuo
@app.get("/individuos/{nombre}")
def consultar_individuo(nombre: str):
    ind = get_thing(nombre)
    datos = {}
    relaciones = {}
    
    for prop in ind.get_properties():
        valores = prop[ind]
        # Separar si es Data o Object property
        if isinstance(prop, ObjectPropertyClass):
            relaciones[prop.python_name] = [v.name for v in valores]
        else:
            # Convertir a str para JSON seguro
            datos[prop.python_name] = [str(v) for v in valores]
            
    return {
        "nombre": ind.name,
        "clase": ind.is_a[0].name,
        "datos": datos,
        "relaciones": relaciones
    }

# 5. Endpoint SPARQL
@app.post("/consultar/sparql")
def consultar_sparql(consulta: SPARQLQuery):
    try:
        # graph.query de owlready2
        results = list(default_world.sparql(consulta.query))
        return {"resultados": results}
    except Exception as e:
        raise HTTPException(400, detail=str(e))


# --- FUNCIONALIDAD EXTRA: Endpoints Específicos por Clase ---

def obtener_detalles_instancias(nombre_clase: str):
    """
    Función auxiliar que recupera todas las instancias de una clase
    y formatea sus datos y relaciones para devolver JSON limpio.
    """
    clase = onto[nombre_clase]
    if not clase:
        return []

    resultados = []
    
    # .instances() obtiene las instancias directas y heredadas
    for ind in clase.instances():
        datos = {}
        relaciones = {}
        
        # Extraemos propiedades dinámicamente
        for prop in ind.get_properties():
            valores = prop[ind]
            # Formateo seguro para JSON
            valores_limpios = [v.name if hasattr(v, 'name') else str(v) for v in valores]
            
            # Separar Data vs Object properties
            if isinstance(prop, ObjectPropertyClass):
                relaciones[prop.python_name] = valores_limpios
            else:
                datos[prop.python_name] = valores_limpios
        
        resultados.append({
            "id": ind.name,
            "tipo": ind.is_a[0].name, # La clase más específica
            "datos": datos,
            "relaciones": relaciones
        })
        
    return resultados

# --- Endpoints GET Específicos ---

@app.get("/libros")
def obtener_todos_los_libros():
    """Devuelve todos los libros con autores y editoriales."""
    return obtener_detalles_instancias("Libro")

@app.get("/revistas")
def obtener_todas_las_revistas():
    """Devuelve todas las revistas."""
    return obtener_detalles_instancias("Revista")

@app.get("/usuarios")
def obtener_todos_los_usuarios():
    """
    Devuelve TODOS los usuarios (incluye Estudiantes y Docentes 
    porque son subclases de Usuario).
    """
    return obtener_detalles_instancias("Usuario")

@app.get("/estudiantes")
def obtener_estudiantes():
    """Devuelve solo los estudiantes."""
    return obtener_detalles_instancias("Estudiante")

@app.get("/docentes")
def obtener_docentes():
    """Devuelve solo los docentes."""
    return obtener_detalles_instancias("Docente")

@app.get("/bibliotecarios")
def obtener_bibliotecarios():
    """Devuelve el personal bibliotecario."""
    return obtener_detalles_instancias("Bibliotecario")

@app.get("/editoriales")
def obtener_editoriales():
    """Devuelve las editoriales y qué libros han publicado."""
    return obtener_detalles_instancias("Editorial")












# --- ENDPOINT MAESTRO DE BÚSQUEDA (FACETED SEARCH) ---
# --- LÓGICA DE BÚSQUEDA INTERNA (Helper Function) ---

def _buscar_en_local(query_str: str, clase_filtro: str = None):
    """
    Función auxiliar que busca en la ontología cargada en memoria.
    Devuelve una lista de diccionarios.
    """
    resultados = []
    q = query_str.lower()
    
    # 1. Definir alcance
    if clase_filtro and onto[clase_filtro]:
        scope = onto[clase_filtro].instances()
    else:
        scope = onto.individuals()

    # 2. Iterar y buscar
    for ind in scope:
        match_found = False
        match_details = ""

        # A. ID
        if q in ind.name.lower():
            match_found = True
            match_details = "Coincidencia en ID"
        
        # B. Labels
        if not match_found and hasattr(ind, "label"):
            for lbl in ind.label:
                if q in lbl.lower():
                    match_found = True
                    match_details = f"Coincidencia en etiqueta: {lbl}"
                    break
        
        # C. Propiedades
        if not match_found:
            props_texto = ["titulo", "nombre", "descripcion", "carrera", "editorial", "autor"]
            for prop_name in props_texto:
                if hasattr(ind, prop_name):
                    vals = getattr(ind, prop_name)
                    for val in vals:
                        if isinstance(val, str) and q in val.lower():
                            match_found = True
                            match_details = f"Coincidencia en {prop_name}: {val}"
                            break
                if match_found: break

        if match_found:
            # Nombre bonito
            display_name = ind.name
            if hasattr(ind, "titulo") and ind.titulo: display_name = ind.titulo[0]
            elif hasattr(ind, "nombre") and ind.nombre: display_name = ind.nombre[0]
            elif ind.label: display_name = ind.label[0]

            resultados.append({
                "id": ind.name,
                "tipo": ind.is_a[0].name,
                "nombre_mostrar": display_name,
                "descripcion": match_details,
                "origen": "Local",   # <--- ETIQUETA CLAVE
                "imagen": None       # Localmente no solemos tener URLs de imágenes
            })
            
    return resultados

# --- ENDPOINTS DE BÚSQUEDA ---

@app.get("/buscador")
def buscador_offline(q: str = Query(..., min_length=1), 
                     clase: Optional[str] = Query(None)):
    """
    Modo Offline: Busca SOLO en el archivo .owl local.
    """
    results = _buscar_en_local(q, clase)
    return {"cantidad": len(results), "resultados": results}

@app.get("/buscador/online")
def buscador_hibrido(q: str = Query(..., min_length=2), 
                     lang: str = Query("es", description="Idioma: 'es' o 'en'")):
    
    print(f"--- Búsqueda Híbrida: '{q}' en idioma '{lang}' ---")

    # 1. Búsqueda Local (Tu ontología)
    # (El buscador local ya busca en todos los labels, así que encontrará "Book" o "Libro")
    resultados_locales = _buscar_en_local(q) 

    # 2. Búsqueda Online (DBpedia)
    resultados_online = []
    try:
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        
        # Consulta SPARQL dinámica según el idioma
        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX bif: <bif:>

        SELECT DISTINCT ?s ?label ?comment ?type ?img
        WHERE {{
          ?s rdfs:label ?label .
          ?label bif:contains "'{q}'" . 
          ?s a ?type .
          
          # --- FILTRO DE IDIOMA DINÁMICO ---
          FILTER (lang(?label) = '{lang}') 
          
          OPTIONAL {{ 
            ?s rdfs:comment ?comment . 
            FILTER (lang(?comment) = '{lang}') 
          }}
          OPTIONAL {{ ?s foaf:depiction ?img }}
          
          FILTER (?type IN (dbo:Person, dbo:Book, dbo:Organisation))
        }}
        LIMIT 10
        """
                
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        sparql.setTimeout(15)
        dbpedia_data = sparql.query().convert()
        
        for r in dbpedia_data["results"]["bindings"]:
            tipo_raw = r["type"]["value"]
            tipo_clean = tipo_raw.split('/')[-1]

            resultados_online.append({
                "id": r["s"]["value"],
                "tipo": tipo_clean, 
                "nombre_mostrar": r["label"]["value"],
                "descripcion": r.get("comment", {}).get("value", "Sin descripción"),
                "origen": "DBpedia",  # <--- ETIQUETA CLAVE
                "imagen": r.get("img", {}).get("value", None)
            })
            
    except Exception as e:
        print(f"Error en DBpedia (se mostrarán solo resultados locales): {e}")
        # Si falla internet, no rompemos todo, solo seguimos con lo local
    
    # 3. Combinar resultados
    # Ponemos los locales primero porque son "nuestros", luego los de internet
    total_resultados = resultados_locales + resultados_online
    
    return {
        "cantidad": len(total_resultados),
        "resultados": total_resultados
    }












@app.get("/config/idioma/{lang_code}")
def obtener_traducciones_schema(lang_code: str):
    """
    Devuelve un diccionario JSON con las traducciones de la estructura (T-Box).
    Ejemplo: Si pides 'en', devuelve {"Bibliotecario": "Librarian", ...}
    """
    if lang_code not in ["es", "en"]:
        raise HTTPException(400, "Idioma no soportado. Use 'es' o 'en'.")
    
    traducciones = {}
    
    # 1. Traducir nombres de Clases
    for cls in onto.classes():
        # Busca el label en el idioma solicitado
        lbl = cls.label.get_by_lang(lang_code)
        if lbl:
            # cls.name es el ID interno (ej: 'Bibliotecario')
            # lbl[0] es la traducción (ej: 'Librarian')
            traducciones[cls.name] = lbl[0]
        else:
            # Si no hay traducción, usamos el nombre original como respaldo
            traducciones[cls.name] = cls.name

    # 2. Traducir nombres de Propiedades
    for prop in onto.properties():
        lbl = prop.label.get_by_lang(lang_code)
        if lbl:
            traducciones[prop.name] = lbl[0]
            
    return traducciones