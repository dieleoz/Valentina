# Roadmap: Tracker Valentina HZ

Progresión de fases para transformar este *tracker* personal en una herramienta web mantenible y editable. Última actualización: 2026-05-15.

---

## Fase 1: Arquitectura Base Vercel ✅ (completada)
*   **[X]** Migración de `localStorage` a base de datos externa (MongoDB).
*   **[X]** Despliegue en Vercel usando *Serverless Functions* (Python/FastAPI).
*   **[X]** Estructuración del repositorio con documentación estándar (README, ARCHITECTURE, ROADMAP).
*   **[X]** Robustez: `replace_one` upsert (no acumula keys huérfanas), `lifespan` (no deprecado), CORS coherente, dead code removido.

---

## Fase 1.5: Editabilidad e Insights ✅ (completada — 2026-05-15)

Respondió las 3 preguntas concretas que motivaron la sesión:

| Pregunta del usuario | Resuelto en |
|---|---|
| "¿Cómo agrego/borro un bloque del registro diario?" | 1.5.1 — Pestaña Hoy, `＋ Bloque` + menú `⋯` |
| "Los libros son muy estáticos — ¿cómo supervisamos?" | 1.5.2 — Biblioteca con estados + `applied_insight` |
| "PDF era para local, ¿no sería Excel incremental para la nube?" | 1.5.3 — `/api/export?format=xlsx&from=...` con 9 hojas long-format |

### 1.5.1 · Categorías editables — `feat/categorias-editables` ✅
*   **[X]** `BLOQUES` constante → `state.plan.categorias` editable. Migración v1→v2 al primer load preservando IDs (`ingles`, `tech`, etc.) → histórico intacto.
*   **[X]** UI: `＋ Bloque`, `✎` (nombre/meta_min/meta_max/color), `⋯` (archivar / eliminar-si-vacía / ↑↓ reordenar). Sección colapsable "Categorías archivadas".
*   **[X]** Archivar preserva histórico; eliminar definitivo solo si no hay registros.
*   **[X]** `renderBloques`, `leerBloquesUI`, `renderResumen7Dias`, `generarPDF*` consumen la lista dinámica.

### 1.5.2 · Biblioteca de libros viva — `feat/biblioteca-libros` ✅
*   **[X]** Estados (`pendiente`/`leyendo`/`pausado`/`terminado`/`abandonado`), progreso por página, fechas de inicio/fin, motivo de abandono, rating.
*   **[X]** `applied_insight` prominente — un libro al 100% sin insight se marca con aviso ámbar "leído sin aplicar".
*   **[X]** Filtros por estado (chips con contador). Agregar libros fuera del plan original (borrables; los originales protegidos).
*   **[X]** Migración v1→v2 idempotente: `name: "X · Y"` → `titulo: "X", autor: "Y"`; `started/finished` → `estado`.
*   **[X]** PDF completo muestra título, autor, estado, progreso e insight (con "leído sin aplicar" si falta).

### 1.5.3 · Export multi-formato + incremental — `feat/export-multiformato` ✅
*   **[X]** Endpoint `GET /api/export?format={xlsx|csv|json}&from=<iso>&to=<iso>`.
*   **[X]** XLSX multi-hoja (9 hojas long-format con freeze + ancho auto). CSV zip. JSON bit-exact reimportable.
*   **[X]** Modo incremental: `?from=<date>` filtra `dias` + `semanas`; catálogos van completos.
*   **[X]** PDF semanal del coach intacto — `generarPDF()` no se tocó en estructura, solo tipografía.
*   **[X]** Frontend: pestaña Datos con date range picker, 3 botones + atajos "Últimos 7 / 30 días".

### Fix post-validación ✅ (`fix/pdf-emojis-idiomas-editables`)
*   **[X]** PDF sin caracteres basura: Helvetica no soporta emoji → reemplazo a texto plano en tabla KPI, secciones de reflexión, coach y biblioteca.
*   **[X]** Idiomas editables: `state.idiomas` migra de objeto plano `{ingles, frances, ielts, tef}` a array `[{id, nombre, nivel, examen_nombre, examen_score, orden}]`. Soporta cualquier idioma con cualquier examen.

---

## Fase 1.6: Features del Plan Maestro (PR #1 — en revisión)

**Origen**: auditoría del tracker vs `plan_maestro_valentina.docx`. Otro agente (Claude Code en cloud) implementó las 6 features en `claude/fix-tracker-plan-gaps-xypvl` (commit `0602d70`) y abrió PR #1 contra `main`.

### Features implementadas (todas con arquitectura "editable por el usuario"):
*   **[X]** **F1 — Monthly KPI Rollup**: pestaña nueva "Mes" con auditoría meta-vs-real. Metas y meses editables desde modal.
*   **[X]** **F2 — Tech Stack Ladder (L0→L6)**: capas dinámicas, reordenables, requieren URL pública para "Completado". Aviso suave (no bloqueante) si se salta capa.
*   **[X]** **F3 — Artefacto público por bloque**: campo obligatorio en bloques de categorías intelectuales. "Ninguno" exige justificación ≥20 chars. Bloques sin artefacto en naranja.
*   **[X]** **F4 — Rutas dinámicas**: 3 rutas precargadas (México, Canadá, AI-Bio), todas editables/pausables/descartables. Cada ruta con textarea "Análisis estratégico". Descartar preserva historial.
*   **[X]** **F5 — Freelance Tier Badge**: tier auto-calculado por reseñas. Umbrales editables.
*   **[X]** **F6 — Filtro de las 6 Verdades**: tool de decisión con verdades editables y umbral configurable. Historial de últimas 20 decisiones.

### Validación local (headless smoke test) ✅
*   **[X]** JS parsea sin errores (brackets balanceados, 188 backticks pares).
*   **[X]** Init renderiza 3 rutas + 7 layers + 6 verdades + 4 meses por defecto.
*   **[X]** `POST /api/state` con nueva shape responde 200 (replace_one funciona).
*   **[X]** Migración idempotente: `cargarEstado` agrega los 6 buckets nuevos si faltan, preserva datos viejos.
*   **[X]** Sin regresión en categorías editables, biblioteca, ni export PDF/XLSX (lo viejo sigue funcionando).

### 🔴 Bugs encontrados en revisión (fix necesario antes/después del merge):

1. **Emojis re-introducidos en PDF** (parcial regresión del fix de 1.5 final):
    * Línea 3989: `'⚠️ X bloques cerraron SIN artefacto público — revisar con el coach'` → ⚠️ no renderiza en Helvetica
    * Línea 4012: rutas se imprimen como `r.emoji + ' ' + r.nombre` — los emojis 🍁🦘🇩🇪 renderizarán basura en la tabla de rutas del PDF
    * Línea 4121 (preexistente, mi fix anterior lo dejó pasar): `'⚠️ leído sin aplicar'` en tabla biblioteca PDF
    * **Fix**: usar el patrón existente — texto plano en PDF, emojis solo en UI

2. **`api/index.py` no actualizado**:
    * Las 6 nuevas state buckets (`metas_mensuales`, `tech_stack_layers`, `rutas_carrera`, `decision_filter`, `freelance_tier`, `artefacto_settings`) no están en `_build_tables`. El export XLSX/CSV las ignora.
    * El export JSON sí las trae (dump bit-exact desde Mongo) → Valentina puede analizarlas en JSON, no en Excel.
    * **Fix**: agregar 6 builders nuevos a `_build_tables` siguiendo el patrón de `categorias` o `libros`.

### Cómo cerrar la fase 1.6:
*   **[ ]** Aplicar los dos fix de arriba (un commit pequeño en la rama del PR antes de mergear, o un commit post-merge en main).
*   **[ ]** Validar PDF semanal generado en producción muestra "PRODUCCIÓN PÚBLICA" + "ESTADO DE RUTAS" sin caracteres basura.
*   **[ ]** Validar export XLSX trae 15 hojas (las 9 existentes + 6 nuevas para las features del Plan Maestro).

---

## Pendientes técnicos identificados durante 1.5 (deuda técnica visible)

Cosas que vi/dejé pasar durante la fase 1.5 y conviene atacar antes que crezcan más:

*   **[ ]** `applied_insight` se edita con `prompt()` nativo desde el aviso ámbar — funcional pero rompe el estilo. El modal de edición ya tiene un textarea bonito; se podría reusarlo con un parámetro `focus=insight`.
*   **[ ]** Auto-vincular bloque "Lectura" con libro vía `@id` en el campo "qué hice": parsear `@grit` y sumar horas a `state.libros[i].horas_total` derivado de la sesión. **Riesgo**: parser de texto libre frágil + doble conteo. Diseñar bien antes de implementar.
*   **[ ]** Hitos (certs/repos) tienen botones `agregar`/`borrar` pero no CRUD completo (no se pueden archivar, no se edita nombre/target). Misma deuda que tenían las categorías antes de 1.5.1.
*   **[ ]** KPIs semanales todavía hardcoded en 9 campos (`postulaciones`, `entrevistas`, etc.). El brief original proponía KPIs editables (PR5). Pendiente — no era una de las 3 preguntas pero es deuda real si el plan cambia.
*   **[ ]** PDF: solución actual es ASCII-only (workaround). Solución correcta sería embeber una fuente TTF Unicode (DejaVu Sans) en jsPDF para soportar emojis y caracteres extendidos sin perder texto.
*   **[ ]** `/api/export?format=json` devuelve `Content-Type: application/json` con `Content-Disposition: attachment` — algunos navegadores lo abren en pestaña en vez de bajarlo cuando se hace GET directo. El `<a>` del frontend lo fuerza, pero curl/browser directo puede sorprender.
*   **[ ]** Sesiones de lectura (`libros[].sesiones`) no implementadas — el modelo está previsto pero por ahora `horas_total` es un campo manual. Cuando se implemente, agregarlo al filtro incremental de `/api/export`.
*   **[ ]** Doc vacío en Mongo devuelve `{}` (2 B) sin las categorías default. Solo afecta a GET directo en un Mongo virgen sin pasar nunca por la UI. Caso límite real pero raro.

---

## Fase 2: Autenticación & Seguridad (siguiente lógica)

**Por qué ahora**: la fase 1.5 hizo el doc Mongo más valioso (CRUD de categorías/libros/idiomas con applied_insight). Hoy CUALQUIERA con la URL puede leer/sobrescribir todo. El endpoint `POST /api/state` no tiene auth.

*   **[ ]** Proteger el Tracker con login básico (password único hashed bcrypt + cookie de sesión).
*   **[ ]** Middleware FastAPI: verificar token/cookie antes de leer o escribir Mongo. 401 si falta.
*   **[ ]** Refactor `USER_ID="valentina"` hardcoded → identificador derivado del token. Prepara terreno para multiusuario.
*   **[ ]** Rate limiting básico en `/api/state` (POST). Vercel tiene KV o se hace con un timestamp en memoria.

---

## Fase 3: Pulido y deuda técnica visible

**Por qué**: la fase 1.5 dejó pendientes concretos (ver sección "Pendientes técnicos identificados"). Atacarlos antes de fase 4 evita acumulación.

*   **[ ]** Hitos editables (certs/repos) — mismo patrón que categorías y libros.
*   **[ ]** KPIs editables — `state.plan.kpis` editable como categorías.
*   **[ ]** Modal con focus selectivo para reemplazar el `prompt()` de `applied_insight`.
*   **[ ]** Auto-vincular `@id` bloque Lectura ↔ sesiones de libro (con tests para evitar doble conteo).
*   **[ ]** Embeber fuente Unicode en jsPDF para PDF con emoji nativo (opcional — workaround actual funciona).

---

## Fase 4: Analítica e IA (alto valor por esfuerzo)

**Por qué**: con el export XLSX ya armado, el JSON semanal listo, y Claude API disponible, esto es el siguiente salto de valor real. El coach (Claude o humano) puede recibir el `/api/export?format=json&from=<lunes>` y devolver análisis estructurado.

*   **[ ]** Endpoint `POST /api/coach-review` que toma `?semana=<lunes>`, llama a Claude API con el JSON de la semana, y devuelve las 5 secciones del coach (lo destacado, áreas a corregir, recomendaciones, riesgos, ajustes al plan).
*   **[ ]** Frontend: botón "🤖 Generar revisión del coach" en pestaña Reporte PDF → llena la sección 6 antes de generar el PDF.
*   **[ ]** Analítica descriptiva con Pandas (regresión horas estudio vs certificaciones logradas). Endpoint `/api/analitica` que devuelve JSON con métricas derivadas.
*   **[ ]** Auto-backup semanal de `/api/export?format=xlsx` a Google Drive (requiere OAuth — más complejo, postergable).

---

## Fase 5: Modernización del frontend (opcional, solo si pesa el monolito)

**Por qué**: `index.html` ya pasa de 2.500 líneas. Si la fase 3 + 4 lo siguen inflando, separar en módulos vale la pena. Pero si el dolor no aparece, no migrar por migrar.

*   **[ ]** Extraer `state.js`, `render.js`, `pdf.js`, `export.js` como módulos ES separados — paso intermedio sin framework.
*   **[ ]** Solo si lo anterior no alcanza: transición a Next.js o Vite + React + Tailwind. Componentes por pestaña.

---

## Fase 6: Dashboard Streamlit (opcional, portafolio)

**Por qué**: vista alternativa en Python puro para demostrar habilidades de Data Science. Lee la misma base Mongo. Útil para portafolio, no para uso diario.

*   **[ ]** `dashboard/app.py` con Streamlit conectado al mismo cluster Mongo. Gráficos de tendencias mensuales, heatmap de consistencia 12 semanas, sparklines por KPI.
