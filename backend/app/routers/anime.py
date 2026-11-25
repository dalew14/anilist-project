
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas


router = APIRouter(
    prefix="/anime",
    tags=["Anime"]
)


# CREATE: Add a new anime
@router.post("/", response_model=schemas.AnimeResponse,
             status_code=status.HTTP_201_CREATED)
def create_anime(anime: schemas.AnimeCreate,
                 db: Session = Depends(get_db)):

    existing_anime = db.query(models.Anime).filter(
        models.Anime.anilist_id == anime.anilist_id
    ).first()

    if existing_anime:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Anime already exists"
        )

    new_anime = models.Anime(**anime.model_dump())

    db.add(new_anime)
    db.commit()
    db.refresh(new_anime)

    return new_anime


# READ: Get all anime
@router.get("/", response_model=list[schemas.AnimeResponse])
def get_all_anime(db: Session = Depends(get_db)):

    return db.query(models.Anime).order_by(
        models.Anime.average_score.desc()
    ).all()


# READ: Get one anime by database ID
@router.get("/{anime_id}", response_model=schemas.AnimeResponse)
def get_anime(anime_id: int, db: Session = Depends(get_db)):

    anime = db.query(models.Anime).filter(
        models.Anime.id == anime_id
    ).first()

    if anime is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anime not found"
        )

    return anime


# UPDATE: Modify an existing anime
@router.put("/{anime_id}", response_model=schemas.AnimeResponse)
def update_anime(anime_id: int,
                 anime: schemas.AnimeUpdate,
                 db: Session = Depends(get_db)):

    existing_anime = db.query(models.Anime).filter(
        models.Anime.id == anime_id
    ).first()

    if existing_anime is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anime not found"
        )

    update_data = anime.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(existing_anime, key, value)

    db.commit()
    db.refresh(existing_anime)

    return existing_anime


# DELETE: Remove an anime
@router.delete("/{anime_id}")
def delete_anime(anime_id: int, db: Session = Depends(get_db)):

    anime = db.query(models.Anime).filter(
        models.Anime.id == anime_id
    ).first()

    if anime is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anime not found"
        )

    db.delete(anime)
    db.commit()

    return {"message": "Anime deleted successfully"}
