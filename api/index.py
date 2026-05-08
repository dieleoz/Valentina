import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict
from pymongo import MongoClient

app = FastAPI(title="Valentina Tracker API")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "")
DB_NAME = "valentina_tracker"
COLLECTION_NAME = "state"

client = None
db = None
collection = None

# We use a single document to store the state, keyed by user_id = 'valentina'
USER_ID = "valentina"

@app.on_event("startup")
def startup_db_client():
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

@app.on_event("shutdown")
def shutdown_db_client():
    if client:
        client.close()

@app.get("/api/state")
async def get_state():
    if collection is None:
        return JSONResponse(status_code=500, content={"message": "Database not configured. Set MONGODB_URI."})
    
    document = collection.find_one({"_id": USER_ID})
    if document:
        # Remove the _id before sending to frontend
        document.pop("_id", None)
        return document
    else:
        # Return empty state if not found (frontend will handle defaults)
        return {}

@app.post("/api/state")
async def save_state(state: Dict[str, Any]):
    if collection is None:
        return JSONResponse(status_code=500, content={"message": "Database not configured. Set MONGODB_URI."})
    
    try:
        # Upsert the state document
        collection.update_one(
            {"_id": USER_ID},
            {"$set": state},
            upsert=True
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving state: {str(e)}")
