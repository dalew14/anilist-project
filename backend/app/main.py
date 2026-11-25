
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import anime


app = FastAPI(
    title="AniList Anime Manager",
    description="API for managing the AniList Top 100 anime database",
    version="1.0.0"
)


# Allow the Flask frontend to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5000",
        "http://localhost:5000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(anime.router)


@app.get("/")
def home():
    return {"message": "AniList Anime Manager API is running!"}
