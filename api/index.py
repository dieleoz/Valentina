import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Any, Dict
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
