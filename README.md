# Tracker Valentina HZ

Aplicación para seguimiento de métricas, hitos y desarrollo profesional para la metodología "Career Architect".

## Características Principales
*   **Registro Diario:** Seguimiento en horas de los bloques clave de la carrera (Inglés, Tech Stack, Freelance, Certificaciones).
*   **KPIs Semanales:** Visualización directa del cumplimiento de métricas duras como Postulaciones, Conexiones en LinkedIn, e Ingresos.
*   **Hitos (Milestones):** Seguimiento del portafolio en GitHub, Certificaciones (Cofepris, ISO, Kaggle), Libros e Idiomas.
*   **Reportes PDF:** Generador de reportes listo para las reuniones semanales de seguimiento con el Coach o mentor.

## Stack Técnico
*   **Frontend:** HTML/CSS/JS clásico.
*   **Backend:** Python con FastAPI (listo para desplegar como Vercel Serverless Function).
*   **Base de datos:** MongoDB Atlas.

## Desarrollo Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/dieleoz/Valentina.git
cd Valentina
```

### 2. Levantar el Backend (API Python)
Asegúrate de tener Python instalado. Luego, instala las dependencias:
```bash
pip install -r requirements.txt
```

Crea un archivo `.env` en el directorio `api/` con tu cadena de conexión a MongoDB:
```
MONGODB_URI="mongodb+srv://USUARIO:PASSWORD@cluster.mongodb.net/?retryWrites=true&w=majority"
```

Inicia el servidor local de FastAPI (Uvicorn):
```bash
uvicorn api.index:app --reload
```
La API estará corriendo en `http://localhost:8000`.

### 3. Levantar el Frontend
Simplemente abre el archivo `index.html` en tu navegador, o usa una extensión como *Live Server* en VS Code. 

*Nota: Para el desarrollo local, el frontend por defecto intentará buscar el backend en su propia raíz. Cuando lo corras con Live Server, es posible que necesites ajustar las rutas de `/api/state` a `http://localhost:8000/api/state` temporalmente, o bien, usar el Vercel CLI (`vercel dev`) que se encarga de unificar los puertos automáticamente.*

## Despliegue en Vercel
1. Ve a [Vercel](https://vercel.com) e importa este repositorio.
2. Selecciona **Python** como Framework Preset (o simplemente deja que Vercel detecte `vercel.json`).
3. En la sección de **Environment Variables**, añade la variable `MONGODB_URI` con tu cadena de conexión.
4. Haz clic en **Deploy**.
