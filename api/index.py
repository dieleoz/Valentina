import os
import io
import csv
import zipfile
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient

MONGODB_URI = os.getenv("MONGODB_URI", "")
DB_NAME = "valentina_tracker"
COLLECTION_NAME = "state"
USER_ID = "valentina"

client = None
db = None
collection = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, db, collection
    if MONGODB_URI:
        try:
            client = MongoClient(MONGODB_URI)
            db = client[DB_NAME]
            collection = db[COLLECTION_NAME]
            print("Connected to MongoDB!")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
    else:
        print("Warning: MONGODB_URI not found. API will return 500 errors if DB is accessed.")
    yield
    if client:
        client.close()


app = FastAPI(title="Valentina Tracker API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/state")
async def get_state():
    if collection is None:
        return JSONResponse(status_code=500, content={"message": "Database not configured. Set MONGODB_URI."})

    document = collection.find_one({"_id": USER_ID})
    if document:
        document.pop("_id", None)
        return document
    return {}


@app.post("/api/state")
async def save_state(state: Dict[str, Any]):
    if collection is None:
        return JSONResponse(status_code=500, content={"message": "Database not configured. Set MONGODB_URI."})

    try:
        doc = {k: v for k, v in state.items() if k != "_id"}
        doc["_id"] = USER_ID
        collection.replace_one({"_id": USER_ID}, doc, upsert=True)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving state: {str(e)}")


# ============= EXPORT (xlsx / csv / json) =============

KPI_FIELDS = [
    ("postulaciones", "Postulaciones formales"),
    ("entrevistas",   "Entrevistas"),
    ("conexiones",    "Conexiones LinkedIn"),
    ("freelance",     "Ingreso freelance USD"),
    ("proyectos",     "Proyectos entregados"),
    ("tarifa",        "Tarifa USD/hr"),
    ("posts",         "Posts LinkedIn (inglés)"),
    ("commits",       "Commits GitHub"),
    ("certs",         "Certificaciones publicadas"),
    ("reflexion",     "Reflexión semanal"),
    ("preguntas",     "Preguntas al coach"),
    ("plan",          "Plan próxima semana"),
]


def _within(date_str: str, from_d: Optional[str], to_d: Optional[str]) -> bool:
    """ISO 8601 date strings sort lexicographically, so we compare directly."""
    if from_d and date_str < from_d:
        return False
    if to_d and date_str > to_d:
        return False
    return True


def _filter_state(state: dict, from_d: Optional[str], to_d: Optional[str]) -> dict:
    if not from_d and not to_d:
        return state
    out = dict(state)
    if isinstance(state.get("dias"), dict):
        out["dias"] = {k: v for k, v in state["dias"].items() if _within(k, from_d, to_d)}
    if isinstance(state.get("semanas"), dict):
        out["semanas"] = {k: v for k, v in state["semanas"].items() if _within(k, from_d, to_d)}
    return out


def _categoria_lookup(state: dict) -> Dict[str, dict]:
    cats = (state.get("plan") or {}).get("categorias") or []
    return {c.get("id"): c for c in cats if isinstance(c, dict)}


def _build_tables(state: dict) -> Dict[str, list]:
    """Each table is a list of dicts (long format) — first item defines the columns."""
    cat_lookup = _categoria_lookup(state)

    # 1. dias — una fila por (fecha × bloque). Wins/blockers se agregan en otra hoja para no inflar.
    dias_rows = []
    notas_rows = []
    for fecha in sorted((state.get("dias") or {}).keys()):
        d = state["dias"][fecha]
        bloques = (d.get("bloques") or {})
        for bid in sorted(bloques.keys()):
            b = bloques[bid] or {}
            cat = cat_lookup.get(bid) or {}
            dias_rows.append({
                "fecha": fecha,
                "bloque_id": bid,
                "bloque_nombre": cat.get("nombre", bid),
                "estado_categoria": cat.get("estado", ""),
                "done": bool(b.get("done")),
                "horas": float(b.get("hours") or 0),
                "que_hice": b.get("what") or "",
            })
        if d.get("wins") or d.get("blockers"):
            notas_rows.append({
                "fecha": fecha,
                "wins": d.get("wins") or "",
                "blockers": d.get("blockers") or "",
            })

    # 2. semanas — una fila por (lunes × kpi)
    semanas_rows = []
    for lunes in sorted((state.get("semanas") or {}).keys()):
        s = state["semanas"][lunes] or {}
        for kpi_id, kpi_label in KPI_FIELDS:
            v = s.get(kpi_id)
            if v in (None, ""):
                continue
            semanas_rows.append({
                "semana_inicio": lunes,
                "kpi_id": kpi_id,
                "kpi_nombre": kpi_label,
                "valor": v,
            })

    # 3. categorias
    categorias_rows = []
    for c in (state.get("plan") or {}).get("categorias") or []:
        if not isinstance(c, dict):
            continue
        categorias_rows.append({
            "id": c.get("id"),
            "nombre": c.get("nombre"),
            "meta_min": c.get("meta_min"),
            "meta_max": c.get("meta_max"),
            "color": c.get("color"),
            "orden": c.get("orden"),
            "estado": c.get("estado"),
            "creado_en": c.get("creado_en"),
            "archivado_en": c.get("archivado_en"),
        })

    # 4. libros
    libros_rows = []
    for l in state.get("libros") or []:
        if not isinstance(l, dict):
            continue
        libros_rows.append({
            "id": l.get("id"),
            "titulo": l.get("titulo") or l.get("name"),
            "autor": l.get("autor"),
            "paginas_total": l.get("paginas_total"),
            "en_plan_original": l.get("en_plan_original"),
            "estado": l.get("estado"),
            "pagina_actual": l.get("pagina_actual"),
            "inicio": l.get("inicio"),
            "fin": l.get("fin"),
            "motivo_abandono": l.get("motivo_abandono"),
            "applied_insight": l.get("applied_insight") or "",
            "horas_total": l.get("horas_total"),
            "rating": l.get("rating"),
            "orden": l.get("orden"),
        })

    # 5. certs
    certs_rows = []
    for c in state.get("certs") or []:
        if not isinstance(c, dict):
            continue
        certs_rows.append({
            "id": c.get("id"),
            "name": c.get("name"),
            "target": c.get("target"),
            "done": c.get("done"),
            "doneDate": c.get("doneDate"),
            "url_curso": c.get("url"),
            "url_certificado": c.get("certUrl"),
        })

    # 6. repos
    repos_rows = []
    for r in state.get("repos") or []:
        if not isinstance(r, dict):
            continue
        repos_rows.append({
            "id": r.get("id"),
            "name": r.get("name"),
            "target": r.get("target"),
            "done": r.get("done"),
            "doneDate": r.get("doneDate"),
            "url_repo": r.get("repoUrl"),
        })

    # 7. idiomas (key/value)
    idiomas_rows = []
    for k, v in (state.get("idiomas") or {}).items():
        idiomas_rows.append({"campo": k, "valor": v})

    # 8. meta plan
    plan = state.get("plan") or {}
    meta_rows = [
        {"campo": "schema_version", "valor": state.get("schema_version", "")},
        {"campo": "plan_nombre", "valor": plan.get("nombre", "")},
        {"campo": "categorias_activas", "valor": sum(1 for c in (plan.get("categorias") or []) if c.get("estado") == "activo")},
        {"campo": "categorias_archivadas", "valor": sum(1 for c in (plan.get("categorias") or []) if c.get("estado") == "archivado")},
        {"campo": "dias_registrados", "valor": len(state.get("dias") or {})},
        {"campo": "semanas_kpi", "valor": len(state.get("semanas") or {})},
        {"campo": "libros_totales", "valor": len(state.get("libros") or [])},
        {"campo": "libros_terminados", "valor": sum(1 for l in (state.get("libros") or []) if l.get("estado") == "terminado")},
    ]

    return {
        "dias": dias_rows,
        "semanas_kpi": semanas_rows,
        "categorias": categorias_rows,
        "libros": libros_rows,
        "certificaciones": certs_rows,
        "repos_github": repos_rows,
        "idiomas": idiomas_rows,
        "notas_diarias": notas_rows,
        "meta_plan": meta_rows,
    }


def _build_csv_zip(state: dict) -> bytes:
    tables = _build_tables(state)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, rows in tables.items():
            sbuf = io.StringIO()
            if rows:
                fieldnames = list(rows[0].keys())
                w = csv.DictWriter(sbuf, fieldnames=fieldnames, extrasaction="ignore")
                w.writeheader()
                for r in rows:
                    w.writerow(r)
            else:
                sbuf.write("(sin registros)\n")
            zf.writestr(f"{name}.csv", sbuf.getvalue())
    return buf.getvalue()


def _build_xlsx(state: dict) -> bytes:
    # Import diferido para arranque más rápido cuando el endpoint no se usa
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment

    tables = _build_tables(state)
    wb = Workbook()
    wb.remove(wb.active)

    header_font = Font(bold=True, color="1F4E79")
    header_fill = PatternFill("solid", fgColor="D9E2F3")

    for name, rows in tables.items():
        ws = wb.create_sheet(title=name[:31])  # límite Excel
        if not rows:
            ws.append(["(sin registros)"])
            continue
        fieldnames = list(rows[0].keys())
        ws.append(fieldnames)
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="left")
        for r in rows:
            ws.append([r.get(k) for k in fieldnames])
        # Ancho aproximado por columna (cap a 40)
        for i, col in enumerate(fieldnames, 1):
            max_len = max([len(str(col))] + [len(str(r.get(col, ""))) for r in rows[:200]])
            ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = min(40, max(10, max_len + 2))
        ws.freeze_panes = "A2"

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


@app.get("/api/export")
async def export_data(
    format: str = Query("json", regex="^(json|csv|xlsx)$"),
    from_date: Optional[str] = Query(None, alias="from", regex=r"^\d{4}-\d{2}-\d{2}$"),
    to_date: Optional[str] = Query(None, alias="to", regex=r"^\d{4}-\d{2}-\d{2}$"),
):
    if collection is None:
        return JSONResponse(status_code=500, content={"message": "Database not configured."})

    doc = collection.find_one({"_id": USER_ID}) or {}
    doc.pop("_id", None)
    filtered = _filter_state(doc, from_date, to_date)

    range_part = ""
    if from_date or to_date:
        range_part = f"_{from_date or 'inicio'}_a_{to_date or 'fin'}"

    if format == "json":
        return JSONResponse(
            filtered,
            headers={"Content-Disposition": f'attachment; filename="valentina{range_part}.json"'},
        )
    if format == "csv":
        data = _build_csv_zip(filtered)
        return Response(
            data,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="valentina{range_part}_csv.zip"'},
        )
    if format == "xlsx":
        data = _build_xlsx(filtered)
        return Response(
            data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="valentina{range_part}.xlsx"'},
        )

    raise HTTPException(status_code=400, detail="format must be json|csv|xlsx")
