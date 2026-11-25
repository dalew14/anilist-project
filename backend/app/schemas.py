
from pydantic import BaseModel, ConfigDict, Field

# Info all the anime share
class AnimeBase(BaseModel):
    title: str = Field(min_length=1)
    average_score: float | None = None
    popularity: int | None = None
    episodes: int | None = None
    release_year: int | None = None
    season: str | None = None
    anime_format: str | None = None
    genres: list[str] | None = None
    description: str | None = None
    anilist_url: str | None = None


# Used when creating an anime
class AnimeCreate(AnimeBase):
    anilist_id: int


# Used when updating an anime
class AnimeUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    average_score: float | None = None
    popularity: int | None = None
    episodes: int | None = None
    release_year: int | None = None
    season: str | None = None
    anime_format: str | None = None
    genres: list[str] | None = None
    description: str | None = None
    anilist_url: str | None = None


# Used when returning anime information
class AnimeResponse(AnimeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    anilist_id: int
