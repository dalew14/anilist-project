
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


# Create a separate in-memory database for testing
TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


# Set up a fresh database for each test
@pytest.fixture
def client():
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


# Sample anime used by the tests
def sample_anime():
    return {
        "anilist_id": 999999999,
        "title": "Test Anime",
        "average_score": 85,
        "popularity": 1000,
        "episodes": 12,
        "release_year": 2026,
        "season": "FALL",
        "anime_format": "TV",
        "genres": ["Action", "Adventure"],
        "description": "Anime used for testing.",
        "anilist_url": "https://anilist.co"
    }


# CREATE test
def test_create_anime(client):
    response = client.post("/anime/", json=sample_anime())

    assert response.status_code == 201
    assert response.json()["title"] == "Test Anime"
    assert response.json()["anilist_id"] == 999999999


# READ ALL test
def test_get_all_anime(client):
    client.post("/anime/", json=sample_anime())

    response = client.get("/anime/")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Test Anime"


# READ ONE test
def test_get_anime(client):
    create_response = client.post("/anime/", json=sample_anime())
    anime_id = create_response.json()["id"]

    response = client.get(f"/anime/{anime_id}")

    assert response.status_code == 200
    assert response.json()["id"] == anime_id
    assert response.json()["title"] == "Test Anime"


# UPDATE test
def test_update_anime(client):
    create_response = client.post("/anime/", json=sample_anime())
    anime_id = create_response.json()["id"]

    update_data = {
        "title": "Updated Test Anime",
        "average_score": 95
    }

    response = client.put(
        f"/anime/{anime_id}",
        json=update_data
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Test Anime"
    assert response.json()["average_score"] == 95


# DELETE test
def test_delete_anime(client):
    create_response = client.post("/anime/", json=sample_anime())
    anime_id = create_response.json()["id"]

    response = client.delete(f"/anime/{anime_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Anime deleted successfully"

    
    get_response = client.get(f"/anime/{anime_id}")
    assert get_response.status_code == 404
