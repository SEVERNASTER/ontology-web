# Sistema de Gestión de Biblioteca Semántica (Ontología OWL)

Este proyecto es una aplicación web full-stack que gestiona una ontología de biblioteca utilizando **Python (FastAPI + Owlready2)** en el backend y **React (Vite)** en el frontend.

El sistema permite la gestión de **Libros, Usuarios, Editoriales y Préstamos** mediante lógica semántica.

---

## 📂 Estructura del Proyecto

El proyecto se divide en dos carpetas principales:

- `/backend`: Contiene la API en Python, la ontología `.owl` y los scripts de poblado.
- `/frontend`: Contiene la interfaz de usuario en React.

---

## 🚀 1. Configuración del Backend

### 1.1. Prerrequisitos

- **Python 3.10+** instalado.


### 1.2. Instalación de dependencias

1. Abre una terminal y navega a la carpeta del backend:

```bash
cd backend
```

2. Instala las dependencias principales del proyecto:

```bash
pip install -r requirements.txt
```


### 1.3. Instalar las librerías necesarias

```bash
pip install -r requirements.txt
```

### 1.4. Librerías adicionales para el script de poblado

```bash
pip install SPARQLWrapper faker
```

## 💾 2. Poblado de Datos (Paso Crítico)

El sistema funciona en dos modos:

- **Offline** → Datos locales dentro de `biblioteca.owl`
- **Online** → Datos consultados desde DBpedia

Para que el modo Offline funcione, es necesario poblar la ontología.

> ⚠️ **Este proceso solo se realiza una vez.**

### 2.1. Generar la estructura vacía

Ejecuta el servidor una vez para generar la ontología base:

```bash
uvicorn main:app --reload
```

Cuando veas que se generó el archivo `.owl`, detén el servidor:

```
Ctrl + C
```

### 2.2. Inyectar datos (poblado)

Con el servidor detenido, ejecuta:

```bash
python poblar_datos.py
```

Este script:

- Descarga libros reales desde internet  
- Genera estudiantes/usuarios falsos  
- Inserta todo en `biblioteca.owl`

### 2.3. Reiniciar o borrar los datos

Si deseas regenerar todo desde cero:

1. Borra `biblioteca.owl` dentro de `/backend`.
2. Repite:
   - **Paso 2.1** → Generar ontología base  
   - **Paso 2.2** → Poblar datos  

## ▶️ 3. Ejecutar el Servidor Backend

Con la ontología lista:

```bash
uvicorn main:app --reload
```

- **API Base:** http://127.0.0.1:8000  
- **Swagger Docs:** http://127.0.0.1:8000/docs

## ⚛️ 4. Ejecutar el Cliente (Frontend)

### 4.1. Prerrequisitos

- Node.js instalado.

### 4.2. Instalación y ejecución

En una nueva terminal:

```bash
cd ontologia-frontend
```

Instalar dependencias:

```bash
npm install
```

Ejecutar servidor de desarrollo:

```bash
npm run dev
```

Abrir la URL que muestra la consola (generalmente):

```
http://localhost:5173
```

## 💡 5. Guía de Uso

### 5.1. Modo Offline (por defecto)

- Las búsquedas se realizan sobre `biblioteca.owl`.
- No requiere internet.
- Consultas rápidas.

### 5.2. Modo Online (DBpedia)

Activa en la interfaz:

```
Buscar en Web / DBpedia
```

- Las consultas se enviarán a DBpedia.
- Requiere internet.
- Puede tardar algunos segundos.



