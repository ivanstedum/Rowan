from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.vectordb import PlantVectorDB


class QueryRequest(BaseModel):
    query: str
    n_results: int = Field(default=3, ge=1, le=20)


db_instance: PlantVectorDB | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_instance
    print("\n" + "=" * 80)
    print("🌱 Rowan - AI Gardening Assistant API")
    print("=" * 80 + "\n")

    print("[MAIN] 🔵 STEP 1: Initializing vector database...")
    db_instance = PlantVectorDB()
    print("[MAIN] ✅ VectorDB initialized\n")

    print("[MAIN] 🔵 STEP 2: Loading plant data...")
    db_instance.load_plants_from_json("./data/plants.json")
    print("[MAIN] ✅ Plant data loaded\n")

    print("[MAIN] ✅ Rowan API startup complete")
    print("=" * 80 + "\n")
    yield


app = FastAPI(title="Rowan API", version="0.1.0", lifespan=lifespan)


@app.get("/")
def root():
    return {"service": "rowan", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/query")
def query_plants(req: QueryRequest):
    if db_instance is None:
        raise HTTPException(status_code=503, detail="Database not initialized")

    raw = db_instance.query_plants(req.query, n_results=req.n_results)

    ids = raw.get("ids", [[]])
    metadatas = raw.get("metadatas", [[]])
    similarities = raw.get("similarities", [[]])

    ordered_plants = []
    first_ids = ids[0] if ids else []
    first_metas = metadatas[0] if metadatas else []
    first_sims = similarities[0] if similarities else []

    for idx, plant_id in enumerate(first_ids):
        meta = first_metas[idx] if idx < len(first_metas) else {}
        sim = first_sims[idx] if idx < len(first_sims) else None
        ordered_plants.append(
            {
                "id": plant_id,
                "name": meta.get("name"),
                "similarity": sim,
                "sun_requirement": meta.get("sun_requirement"),
                "water_needs": meta.get("water_needs"),
                "hardiness_zones": meta.get("hardiness_zones"),
            }
        )

    return ordered_plants


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8081)
