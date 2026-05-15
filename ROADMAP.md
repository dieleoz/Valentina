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

### 1.5.1 · Categorías editables — `feat/categorias-editables` ✅
*   **[X]** Migrar `BLOQUES` (constante hardcodeada) a `state.plan.categorias` (editable, en Mongo).
*   **[X]** Migración automática: si el doc no tiene `plan.categorias`, generarlo desde los 6 IDs originales (`ingles`, `tech`, `empleo`, `certs`, `freelance`, `lectura`). IDs estables → histórico intacto.
*   **[X]** UI: botón `＋ Bloque` (agregar), `✎` (renombrar nombre/meta_min/meta_max/color), `⋯` (archivar / eliminar si no hay registros / ↑↓ reordenar).
*   **[X]** Archivar preserva histórico (los días viejos siguen mostrando "Inglés 1.5h" aunque el bloque ya no aparezca en "Hoy").
*   **[X]** Eliminar definitivo solo si no hay días con `hours > 0` en esa categoría.
*   **[X]** Sección colapsable "Categorías archivadas" al final del listado.
*   **[X]** `renderBloques`, `leerBloquesUI`, `renderResumen7Dias`, `generarPDF*` consumen la lista dinámica.
*   **[X]** Validación: agregar/renombrar/archivar en deploy live, histórico intacto, PDF semanal idéntico. Mergeado 2026-05-15.

### 1.5.2 · Biblioteca de libros viva — `feat/biblioteca-libros` ✅
*   **[X]** Modelo de libros con estados (`pendiente`/`leyendo`/`pausado`/`terminado`/`abandonado`), progreso por página, fechas de inicio/fin, motivo de abandono, rating.
*   **[X]** Campo `applied_insight` prominente — un libro al 100% sin `applied_insight` se marca con aviso ámbar "leído sin aplicar".
*   **[X]** Filtros por estado (chips con contador), agregar libros fuera del plan original (borrables; los originales protegidos).
*   **[X]** Migración v1→v2 idempotente: `name: "X · Y"` → `titulo: "X", autor: "Y"`; `started/finished` → `estado`.
*   **[X]** PDF completo de hitos muestra título, autor, estado, progreso e insight (con "⚠️ leído sin aplicar" si falta).
*   **[X]** Validación: estados, applied_insight, migración v1→v2 verificada con dump v1 simulado en headless. Mergeado 2026-05-15.
*   **[~]** Diferido: vínculo automático con bloque "Lectura" via `@id` para evitar parser frágil y doble conteo. Horas se editan a mano en el modal.

### 1.5.3 · Export multi-formato + incremental — `feat/export-multiformato` ✅
*   **[X]** Endpoint `GET /api/export?format={xlsx|csv|json}&from=<iso>&to=<iso>`.
*   **[X]** Excel multi-hoja (9 hojas: días, semanas_kpi, categorias, libros, certificaciones, repos_github, idiomas, notas_diarias, meta_plan) en formato long con freeze de primera fila y ancho auto-ajustado.
*   **[X]** CSV zip (un CSV por tabla), JSON bit-exact servido desde backend (reimportable via Importar respaldo).
*   **[X]** Modo incremental: `?from=<date>` filtra `state.dias` y `state.semanas` por fecha lexicográfica. Catálogos (categorías, libros, etc.) se entregan completos.
*   **[X]** PDF semanal del coach permanece **idéntico** (sin tocar `generarPDF()`).
*   **[X]** Frontend: pestaña Datos con date range picker, 3 botones de formato y atajos "Últimos 7 / 30 días".
*   **[X]** Validación: XLSX abre limpio (verificado en openpyxl); CSV zip con 9 archivos; incremental filtra `from=2026-05-05` → solo días posteriores. Mergeado 2026-05-15.

---

## Fase 1.5 ✅ COMPLETADA

Las 3 sub-fases mergeadas a `main`:
1. Categorías editables (bloques CRUD + archivar/eliminar)
2. Biblioteca de libros viva (estados + applied_insight + migración v1→v2)
3. Export multi-formato + incremental (XLSX/CSV/JSON, /api/export)

Fix post-validación (mergeado 2026-05-15):
*   **[X]** PDF sin caracteres basura: Helvetica no soporta emoji → reemplazo por texto plano en tabla KPI, secciones de reflexión, coach y biblioteca.
*   **[X]** Idiomas editables: `state.idiomas` migra de objeto plano (`{ingles, frances, ielts, tef}`) a array `[{id, nombre, nivel, examen_nombre, examen_score, orden}]`. Soporta cualquier idioma con cualquier examen — no más hardcoded Inglés/Francés.

El stack se mantuvo vanilla JS + FastAPI + Mongo. El PDF del coach quedó intacto en estructura, sólo se limpió la tipografía.

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
