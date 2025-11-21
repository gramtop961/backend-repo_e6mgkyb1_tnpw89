import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from database import create_document, get_documents, db

app = FastAPI(title="Comic Stream API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SeriesIn(BaseModel):
    title: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    banner_url: Optional[str] = None
    genres: List[str] = []
    rating: Optional[float] = 0.0
    featured: bool = False
    creator_ids: List[str] = []

class EpisodeIn(BaseModel):
    series_id: str
    title: str
    synopsis: Optional[str] = None
    thumb_url: Optional[str] = None
    video_url: Optional[str] = None
    episode_number: int
    season: Optional[int] = 1
    duration_sec: Optional[int] = None

@app.get("/")
def read_root():
    return {"message": "Comic Stream API running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

@app.get("/api/series")
def list_series(limit: int = 20):
    docs = get_documents("series", {}, limit)
    for d in docs:
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
    return {"items": docs}

@app.post("/api/series")
def create_series(payload: SeriesIn):
    try:
        new_id = create_document("series", payload.model_dump())
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/series/{series_id}/episodes")
def list_episodes(series_id: str, limit: int = 50):
    docs = get_documents("episode", {"series_id": series_id}, limit)
    for d in docs:
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
    return {"items": docs}

@app.post("/api/episodes")
def create_episode(payload: EpisodeIn):
    try:
        new_id = create_document("episode", payload.model_dump())
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/seed")
def seed_sample_data():
    """Insert a small set of demo series/episodes to get started"""
    try:
        # Only seed if empty
        existing = get_documents("series", {}, limit=1)
        if existing:
            return {"status": "ok", "message": "Series already exist. Skipping seed."}

        demo_series = [
            {
                "title": "Shield of Valor",
                "description": "A lone guardian defends the city with an ancient shield of untold power.",
                "cover_url": "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?q=80&w=1200&auto=format&fit=crop",
                "banner_url": "https://images.unsplash.com/photo-1517466787929-bc90951d0974?q=80&w=1600&auto=format&fit=crop",
                "genres": ["Superhero", "Action"],
                "rating": 4.6,
                "featured": True,
                "creator_ids": []
            },
            {
                "title": "Neon Nightwatch",
                "description": "Cyber-noir vigilantes patrol a city of light and secrets.",
                "cover_url": "https://images.unsplash.com/photo-1520976229190-1c1cf303d4e9?q=80&w=1200&auto=format&fit=crop",
                "banner_url": "https://images.unsplash.com/photo-1520975730396-2f9b36e636b2?q=80&w=1600&auto=format&fit=crop",
                "genres": ["Sci-Fi", "Thriller"],
                "rating": 4.4,
                "featured": False,
                "creator_ids": []
            },
            {
                "title": "Arcane Academy",
                "description": "Students master spells and secrets at a mysterious academy.",
                "cover_url": "https://images.unsplash.com/photo-1519681393784-d120267933ba?q=80&w=1200&auto=format&fit=crop",
                "banner_url": "https://images.unsplash.com/photo-1495461199391-8c39f6b4a3a5?q=80&w=1600&auto=format&fit=crop",
                "genres": ["Fantasy", "Adventure"],
                "rating": 4.7,
                "featured": False,
                "creator_ids": []
            }
        ]

        ids = []
        for s in demo_series:
            new_id = create_document("series", s)
            ids.append(new_id)

        # Add a couple of episodes for first series
        ep_payloads = [
            {
                "series_id": ids[0],
                "title": "Pilot: Rise of the Shield",
                "synopsis": "An unexpected hero inherits a legendary shield.",
                "thumb_url": demo_series[0]["cover_url"],
                "video_url": None,
                "episode_number": 1,
                "season": 1,
                "duration_sec": 720
            },
            {
                "series_id": ids[0],
                "title": "Echoes in Steel",
                "synopsis": "The city trembles as a new villain emerges.",
                "thumb_url": demo_series[0]["cover_url"],
                "video_url": None,
                "episode_number": 2,
                "season": 1,
                "duration_sec": 690
            }
        ]
        for ep in ep_payloads:
            create_document("episode", ep)

        return {"status": "ok", "inserted_series": len(ids), "inserted_episodes": len(ep_payloads)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
