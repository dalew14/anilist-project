
import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen

from sqlalchemy.orm import Session


# Locate the project and backend folders
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"

sys.path.insert(0, str(BACKEND_DIR))

from app.database import Base, engine
from app.models import Anime


# AniList GraphQL API
ANILIST_URL = "https://graphql.anilist.co"

QUERY = """
query ($page: Int, $perPage: Int) {
    Page(page: $page, perPage: $perPage) {
        media(
            type: ANIME,
            sort: SCORE_DESC,
            isAdult: false
        ) {
            id
            title {
                english
                romaji
            }
            averageScore
            popularity
            episodes
            seasonYear
            season
            format
            genres
            description(asHtml: false)
            siteUrl
        }
    }
}
"""


def fetch_anime(page):
    """Retrieve one page of anime from AniList."""

    payload = {
        "query": QUERY,
        "variables": {
            "page": page,
            "perPage": 50
        }
    }

    request = Request(
        ANILIST_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "AniListAnimeManager/1.0"
        },
        method="POST"
    )

    with urlopen(request, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))

    if "errors" in result:
        raise RuntimeError(f"AniList API error: {result['errors']}")

    return result["data"]["Page"]["media"]


def import_anime():
    """Import the 100 highest-scoring non-adult anime."""

    Base.metadata.create_all(bind=engine)

    imported_count = 0

    with Session(engine) as db:

        for page in range(1, 3):
            print(f"Retrieving AniList page {page}...")

            anime_list = fetch_anime(page)

            for item in anime_list:

                title = (
                    item["title"]["english"]
                    or item["title"]["romaji"]
                    or "Unknown"
                )

                existing = db.query(Anime).filter(
                    Anime.anilist_id == item["id"]
                ).first()

                anime_data = {
                    "anilist_id": item["id"],
                    "title": title,
                    "average_score": item["averageScore"],
                    "popularity": item["popularity"],
                    "episodes": item["episodes"],
                    "release_year": item["seasonYear"],
                    "season": item["season"],
                    "anime_format": item["format"],
                    "genres": item["genres"],
                    "description": item["description"],
                    "anilist_url": item["siteUrl"]
                }

                if existing:
                    for key, value in anime_data.items():
                        setattr(existing, key, value)
                else:
                    db.add(Anime(**anime_data))

                imported_count += 1

        db.commit()

    print("\nImport completed successfully!")
    print(f"Processed {imported_count} anime.")
    print(f"Database location: {PROJECT_ROOT / 'data' / 'anilist.db'}")


if __name__ == "__main__":
    try:
        import_anime()
    except Exception as error:
        print(f"\nImport failed: {error}")
