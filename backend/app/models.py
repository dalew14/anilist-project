
from sqlalchemy import Column, Integer, String, Float, Text, JSON

from app.database import Base


class Anime(Base):
    __tablename__ = "anime"

    id = Column(Integer, primary_key=True, index=True)

    # Original AniList information
    anilist_id = Column(Integer, unique=True, nullable=False)

    # Anime information
    title = Column(String, nullable=False)
    average_score = Column(Float, nullable=True)
    popularity = Column(Integer, nullable=True)
    episodes = Column(Integer, nullable=True)

    # Release information
    release_year = Column(Integer, nullable=True)
    season = Column(String, nullable=True)
    anime_format = Column(String, nullable=True)

    # Other info
    genres = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    anilist_url = Column(String, nullable=True)
