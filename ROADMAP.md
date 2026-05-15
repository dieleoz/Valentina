# Roadmap: Tracker Valentina HZ

Progresión de fases para transformar este *tracker* personal en una herramienta web mantenible y editable.

---

## Fase 1: Arquitectura Base Vercel ✅
*   **[X]** Migración de `localStorage` a base de datos externa (MongoDB).
*   **[X]** Despliegue en Vercel usando *Serverless Functions* (Python/FastAPI).
*   **[X]** Estructuración del repositorio con documentación estándar (README, ARCHITECTURE, ROADMAP).
*   **[X]** Fixes de robustez: `replace_one` upsert (sin keys huérfanas), `lifespan` (no deprecado), CORS coherente, dead code removido.

---

## Fase 1.5: Editabilidad e Insights (v2) — *en curso*

> Responde tres huecos detectados en auditoría: no se pueden editar bloques, los libros son una checklist estática, y el único export es PDF local (no permite backup ni análisis).
> Tres ramas independientes, cada una se mergea cuando pasa validación.

### 1.5.1 · Categorías editables — `feat/categorias-editables`
*   **[ ]** Migrar `BLOQUES` (constante hardcodeada) a `state.plan.categorias` (editable, en Mongo).
*   **[ ]** Migración automática: si el doc no tiene `plan.categorias`, generarlo desde los 6 IDs originales (`ingles`, `tech`, `empleo`, `certs`, `freelance`, `lectura`). IDs estables → histórico intacto.
*   **[ ]** UI: botón `＋ Bloque` (agregar), `✎` (renombrar nombre/meta_min/meta_max/color), `⋯` (archivar / eliminar si no hay registros / ↑↓ reordenar).
*   **[ ]** Archivar preserva histórico (los días viejos siguen mostrando "Inglés 1.5h" aunque el bloque ya no aparezca en "Hoy").
*   **[ ]** Eliminar definitivo solo si no hay días con `hours > 0` en esa categoría.
*   **[ ]** Sección colapsable "Categorías archivadas" al final del listado.
*   **[ ]** `renderBloques`, `leerBloquesUI`, `renderResumen7Dias`, `generarPDF*` consumen la lista dinámica.
*   **[ ]** Validación: agregar/renombrar/archivar en deploy live, histórico intacto, PDF semanal idéntico.

### 1.5.2 · Biblioteca de libros viva — `feat/biblioteca-libros`
*   **[ ]** Modelo de libros con estados (`pendiente`/`leyendo`/`pausado`/`terminado`/`abandonado`), progreso por página, fechas de inicio/fin, sesiones, motivo de abandono.
*   **[ ]** Campo `applied_insight` prominente — un libro al 100% sin `applied_insight` se marca visualmente como "leído sin aplicar".
*   **[ ]** Filtros por estado (chips), agregar libros fuera del plan original, vínculo opcional con el bloque "Lectura" para sumar horas.
*   **[ ]** Una sola fuente para horas de lectura: el bloque registra, las sesiones del libro se derivan — no se duplica.
*   **[ ]** Validación: cambio de estados, applied_insight persiste, horas no se doble-contabilizan.

### 1.5.3 · Export multi-formato + incremental — `feat/export-multiformato`
*   **[ ]** Endpoint `GET /api/export?format={xlsx|csv|json}&from=<iso>&to=<iso>`.
*   **[ ]** Excel multi-hoja (días, semanas, categorías, kpis, hitos, libros, sesiones, plan) en formato long.
*   **[ ]** CSV zip (un CSV por tabla), JSON bit-exact (re-importable).
*   **[ ]** Modo incremental: `?from=<date>` filtra solo registros con fecha posterior — soporta backup que solo descarga lo nuevo.
*   **[ ]** PDF semanal del coach permanece **idéntico** (regresión test visual).
*   **[ ]** Validación: XLSX abre en Sheets/LibreOffice/Excel; incremental filtra correctamente; PDF sin cambios.

---

## Fase 2: Autenticación & Seguridad
*   **[ ]** Proteger el Tracker con contraseña o login básico.
*   **[ ]** Middleware FastAPI con tokens (JWT o sesión) antes de leer/escribir en Mongo.
*   **[ ]** Refactor de `USER_ID="valentina"` hardcoded → identificador derivado del token.

## Fase 3: Modernización del Frontend
*   **[ ]** Transición del monolito `index.html` a Next.js o Vite + React.
*   **[ ]** Tailwind CSS para diseño más refinado y mantenible.
*   **[ ]** Componentes por pestaña: `<TableroDiario />`, `<TableroSemanal />`, `<Hitos />`, `<Biblioteca />`, `<Datos />`.

## Fase 4: Analítica Avanzada e IA (Python)
*   **[ ]** Analítica descriptiva con Pandas (regresión horas estudio vs certificaciones logradas).
*   **[ ]** Feedback del coach por IA — enviar el JSON semanal a Claude para rellenar "Revisión del Coach" en el PDF.
*   **[ ]** Auto-backup semanal del export incremental a Google Drive (requiere OAuth).

## Fase 5: Dashboard Nativo en Streamlit (opcional)
*   **[ ]** Vista alternativa en `dashboard/` con Streamlit, leyendo la misma base Mongo. Útil para portafolio de Data Science.
