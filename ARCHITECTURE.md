# Arquitectura del Sistema: Tracker Valentina HZ

## Resumen General
El "Tracker Valentina HZ" es una aplicación web *Single Page Application* (SPA) diseñada para realizar un seguimiento riguroso de la ejecución del "Plan Maestro" (Método Grit-Mindset-Carlos-Style). 

## Stack Tecnológico

El sistema ha sido diseñado para operar en un entorno *Serverless* (Vercel) para asegurar costo cero, escalabilidad inmediata y nulo mantenimiento de servidores (Sin VPS).

### 1. Frontend (Cliente)
*   **Lenguajes:** HTML5, CSS3, Vanilla JavaScript.
*   **Patrón de Diseño:** SPA. La interfaz no recarga entre pestañas (Hoy, Semana, Hitos, etc.).
*   **Generación de PDFs:** Librería `jspdf` (y `jspdf-autotable`) inyectada vía CDN para generar reportes dinámicos en el navegador sin carga de servidor.

### 2. Backend (Servidor)
*   **Framework:** FastAPI (Python 3.9+).
*   **Hosting:** Vercel Serverless Functions. El código se encuentra en el directorio `/api`. Vercel enruta todas las peticiones a este servidor Python efímero de manera nativa.

### 3. Persistencia de Datos (Base de Datos)
*   **Proveedor:** MongoDB Atlas.
*   **Driver:** `pymongo`.
*   **Estructura:** Se almacena un documento JSON masivo único que representa todo el "Estado Global" (`state`) del tracker de Valentina. Esto facilita enormemente la lectura/escritura y hace muy trivial el backup manual.

## Flujo de Datos

1.  **Inicialización:** Al cargar `index.html`, el frontend realiza un `GET /api/state`. Si la llamada es exitosa, se hidrata la interfaz con los datos de MongoDB. Si falla (o no hay red), se usa un estado por defecto vacío.
2.  **Escritura (Save):** Cada vez que la usuaria presiona "Guardar día" o marca un hito, la función asíncrona `guardar()` se dispara enviando el árbol completo del estado mediante un `POST /api/state`. 
3.  **Persistencia:** La API de Python recibe el JSON y hace un "Upsert" (Update/Insert) en MongoDB, garantizando que siempre se mantenga la última versión maestra.

## Diagrama de Despliegue en Vercel

```mermaid
graph TD
    User([Usuario/Valentina]) --> Vercel_CDN[Vercel Edge Network]
    Vercel_CDN -- "GET /" --> StaticHTML[index.html (HTML/JS/CSS)]
    Vercel_CDN -- "/api/*" --> PythonFunc[Serverless Function: FastAPI]
    PythonFunc <--> MongoDB[(MongoDB Atlas)]
```
