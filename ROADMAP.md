# Roadmap: Tracker Valentina HZ

Este documento enlista la progresión de fases de desarrollo planeadas para transformar este *tracker* personal en una herramienta web completa.

## Fase 1: Arquitectura Base Vercel (Actual)
*   **[X]** Migración de `localStorage` a base de datos externa (MongoDB).
*   **[X]** Despliegue en Vercel usando *Serverless Functions* (Python/FastAPI).
*   **[X]** Estructuración del repositorio con documentación estándar (README, ARCHITECTURE, ROADMAP).

## Fase 2: Autenticación & Seguridad
*   **[ ]** Proteger el Tracker con una contraseña o inicio de sesión básico.
*   **[ ]** Implementar middleware en FastAPI para verificar tokens de acceso (JWT o sesión) antes de leer o escribir en MongoDB.

## Fase 3: Modernización del Frontend
*   **[ ]** Transición del archivo monolitico `index.html` a un Framework Reactivo (Next.js o Vite con React).
*   **[ ]** Implementación de Tailwind CSS para un diseño visual más refinado y mantenible.
*   **[ ]** Dividir componentes por pestañas: `<TableroDiario />`, `<TableroSemanal />`, `<Hitos />`.

## Fase 4: Analítica Avanzada e IA (Python)
Aprovechando que el backend está en Python, se pueden integrar librerías de Data Science (Pandas) e IA:
*   **[ ]** Analítica descriptiva: Devolver métricas procesadas (ej. regresión lineal de las horas de estudio vs resultados en certificaciones).
*   **[ ]** Feedback del Coach por IA: Enviar el JSON de la semana a un modelo como GPT-4 o Claude 3.5 desde el backend para rellenar automáticamente la sección "Revisión del Coach" en el PDF.

## Fase 5: Dashboard Nativo en Streamlit (Opcional/Alternativo)
*   **[ ]** Crear una vista alternativa en `dashboard/` usando **Streamlit**, leyendo la misma base de datos de MongoDB. Ideal para que Valentina demuestre habilidades puras de Python y Data Science en su portafolio.
