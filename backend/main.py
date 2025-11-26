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
    """Define la estructura de clases y propiedades si no existen."""
    global onto
    
    # Cargar o Crear
    if not os.path.exists(ONTO_FILE):
        print(f"--- Creando ontología desde cero: {ONTO_FILE} ---")
        onto = get_ontology(IRI_BASE)
    else:
        print(f"--- Cargando ontología existente ---")
        onto = get_ontology(ONTO_FILE).load()

    with onto:
        # 1. Definición de Clases Principales
        class Persona(Thing): pass
        class Organizacion(Thing): pass
        class Publicacion(Thing): pass # Clase padre para libros, revistas, etc.
        
        # 2. Subclases de Persona
        class Bibliotecario(Persona): pass
        class Usuario(Persona): pass
        class Docente(Usuario): pass
        class Estudiante(Usuario): pass
        
        # 3. Subclases de Organización
        class Biblioteca(Organizacion): pass
        class Editorial(Organizacion): pass
        
        # 4. Subclases de Publicación
        class Libro(Publicacion): pass
        class PublicacionPeriodica(Publicacion): pass
        class Revista(PublicacionPeriodica): pass
        class Periodico(PublicacionPeriodica): pass

        # 5. Propiedades de Datos (Atributos - DataProperties)
        # Generales
        class nombre(DataProperty): range = [str]
        class direccion(DataProperty): range = [str]
        class telefono(DataProperty): range = [str]
        class email(DataProperty): range = [str]
        class fecha_registro(DataProperty): range = [datetime.date]
        
        # Específicas de Persona/Usuario
        class ci(DataProperty): range = [str] # Carnet
        class fecha_nacimiento(DataProperty): range = [datetime.date]
        class codigo_usuario(DataProperty): range = [str]
        class estado_cuenta(DataProperty): range = [str] # Activo/Suspendido
        
        # Específicas de Estudiante/Docente
        class codigo_sis(DataProperty): domain = [Estudiante]; range = [str]
        class carrera(DataProperty): domain = [Estudiante]; range = [str]
        class item_docente(DataProperty): domain = [Docente]; range = [str]
        class departamento(DataProperty): domain = [Docente]; range = [str]
        
        # Específicas de Bibliotecario
        class id_empleado(DataProperty): domain = [Bibliotecario]; range = [str]
        class turno(DataProperty): range = [str]
        
        # Específicas de Publicación/Libro
        class titulo(DataProperty): range = [str]
        class isbn(DataProperty): domain = [Libro]; range = [str]
        class anio_publicacion(DataProperty): range = [int]
        class numero_paginas(DataProperty): range = [int]
        class estado_libro(DataProperty): range = [str] # Disponible/Prestado
        class resumen(DataProperty): range = [str]
        
        # Específicas de Revista/Periodico
        class issn(DataProperty): range = [str]
        class periodicidad(DataProperty): range = [str] # Mensual, Semanal
        class volumen(DataProperty): range = [int]

        # Específicas de Editorial
        class sitio_web(DataProperty): domain = [Editorial]; range = [str]
        class pais_origen(DataProperty): range = [str]

        # 6. Propiedades de Objeto (Relaciones - ObjectProperties)
        
        # Relaciones de Publicación
        class publica(ObjectProperty):
            domain = [Editorial]
            range = [Publicacion]
            
        class escribe(ObjectProperty):
            domain = [Persona] # Un autor es una persona
            range = [Publicacion]
            
        # Relaciones de Préstamos
        class toma_prestado(ObjectProperty):
            domain = [Usuario]
            range = [Libro]
            
        class gestiona(ObjectProperty):
            domain = [Bibliotecario]
            range = [Thing] # Gestiona prestamos, multas, etc.

        class trabaja_en(ObjectProperty):
            domain = [Bibliotecario]
            range = [Biblioteca]

    # Guardar estructura inicial
    onto.save(file=ONTO_FILE)
    print("--- Estructura de Ontología inicializada correctamente ---")

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

@app.get("/buscador")
def buscador_semantico(q: str = Query(..., min_length=1, description="Texto a buscar"), clase: Optional[str] = Query(None, description="Filtro de clase (Ej: Libro, Estudiante)")):
    """
    Buscador unificado. 
    - Si 'clase' es null: Busca en TODA la ontología.
    - Si 'clase' tiene valor: Filtra solo esa categoría.
    - Busca en: ID (IRI), Etiquetas (Label) y Propiedades de Datos (título, nombre).
    """
    resultados = []
    query_str = q.lower()
    
    # 1. Definir el alcance de búsqueda
    if clase and onto[clase]:
        # Si hay filtro, buscamos solo en esa clase (y sus subclases)
        scope = onto[clase].instances()
    else:
        # Si no, buscamos en todos los individuos de la ontología
        scope = onto.individuals()

    # 2. Iterar y buscar
    for ind in scope:
        match_found = False
        match_details = ""

        # A. Buscar en el ID (IRI)
        if query_str in ind.name.lower():
            match_found = True
            match_details = "Coincidencia en ID"
        
        # B. Buscar en Labels (Etiquetas multilingües si existen)
        if not match_found and hasattr(ind, "label"):
            for lbl in ind.label:
                if query_str in lbl.lower():
                    match_found = True
                    match_details = f"Coincidencia en etiqueta: {lbl}"
                    break
        
        # C. Buscar en Propiedades comunes (titulo, nombre)
        if not match_found:
            # Lista de propiedades donde queremos buscar texto
            props_texto = ["titulo", "nombre", "descripcion", "carrera", "editorial", "autor"]
            for prop_name in props_texto:
                if hasattr(ind, prop_name):
                    vals = getattr(ind, prop_name)
                    # vals suele ser una lista en owlready2
                    for val in vals:
                        if isinstance(val, str) and query_str in val.lower():
                            match_found = True
                            match_details = f"Coincidencia en {prop_name}: {val}"
                            break
                if match_found: break

        # 3. Si hubo coincidencia, agregar al resultado
        if match_found:
            # Intentamos obtener un "Nombre legible" para mostrar en la UI
            display_name = ind.name
            if hasattr(ind, "titulo") and ind.titulo: display_name = ind.titulo[0]
            elif hasattr(ind, "nombre") and ind.nombre: display_name = ind.nombre[0]
            elif ind.label: display_name = ind.label[0]

            resultados.append({
                "id": ind.name,
                "tipo": ind.is_a[0].name, # La clase principal
                "nombre_mostrar": display_name,
                "razon_match": match_details
            })

    return {"cantidad": len(resultados), "resultados": resultados}








    # --- ENDPOINT BÚSQUEDA ONLINE (DBpedia) ---

@app.get("/buscador/online")
def buscar_en_dbpedia(q: str = Query(..., min_length=2, description="Término a buscar en DBpedia")):
    """
    Consulta OPTIMIZADA a DBpedia usando índice de texto completo.
    """
    print(f"--- Consultando DBpedia para: {q} ---")
    
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    
    # TRUCO DE OPTIMIZACIÓN:
    # Usamos 'bif:contains' que es el buscador nativo de Virtuoso (el motor de DBpedia).
    # Es 100 veces más rápido que usar FILTER(CONTAINS(...)).
    
    query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>

    SELECT DISTINCT ?s ?label ?comment ?type ?img
    WHERE {{
      # Búsqueda rápida usando índice full-text
      ?s rdfs:label ?label .
      ?label bif:contains "'{q}'" . 
      
      ?s a ?type .
      
      # Solo etiquetas en español
      FILTER (lang(?label) = 'es')
      
      OPTIONAL {{ 
        ?s rdfs:comment ?comment . 
        FILTER (lang(?comment) = 'es') 
      }}
      OPTIONAL {{ ?s foaf:depiction ?img }}
      
      # Filtramos tipos relevantes
      FILTER (?type IN (dbo:Person, dbo:Book, dbo:Writer, dbo:Organisation, dbo:University, dbo:City))
    }}
    LIMIT 10
    """

    try:
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        sparql.setTimeout(20) # Aumentamos el tiempo de espera a 20 segundos
        results = sparql.query().convert()
        
        resultados_formateados = []
        
        for r in results["results"]["bindings"]:
            tipo_raw = r["type"]["value"]
            tipo_clean = tipo_raw.split('/')[-1]

            resultados_formateados.append({
                "id": r["s"]["value"],
                "tipo": tipo_clean, 
                "nombre_mostrar": r["label"]["value"],
                "descripcion": r.get("comment", {}).get("value", "Sin descripción"),
                "imagen": r.get("img", {}).get("value", None),
                "origen": "DBpedia (Online)"
            })
            
        return {
            "cantidad": len(resultados_formateados),
            "resultados": resultados_formateados
        }

    except Exception as e:
        print(f"Error conectando a DBpedia: {e}")
        # Devolvemos un error limpio para que el frontend no colapse
        return {"cantidad": 0, "resultados": [], "mensaje_error": "DBpedia está lenta, intenta de nuevo."}