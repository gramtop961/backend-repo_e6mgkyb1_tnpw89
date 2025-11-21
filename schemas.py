"""
Database Schemas for the Comic Streaming App

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- Series -> "series"
- Episode -> "episode"
- Creator -> "creator"
"""

from pydantic import BaseModel, Field
from typing import Optional, List

class Creator(BaseModel):
    """
    Creators collection schema
    """
    name: str = Field(..., description="Creator name")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    bio: Optional[str] = Field(None, description="Short bio")
    social: Optional[dict] = Field(default_factory=dict, description="Social links")

class Series(BaseModel):
    """
    Series collection schema
    """
    title: str = Field(..., description="Series title")
    description: Optional[str] = Field(None, description="Series description")
    cover_url: Optional[str] = Field(None, description="Cover poster URL")
    banner_url: Optional[str] = Field(None, description="Wide banner URL")
    genres: List[str] = Field(default_factory=list, description="List of genres")
    rating: Optional[float] = Field(default=0.0, ge=0, le=5, description="Average rating 0-5")
    featured: bool = Field(default=False, description="Whether series is featured on home")
    creator_ids: List[str] = Field(default_factory=list, description="List of creator ids")

class Episode(BaseModel):
    """
    Episode collection schema
    """
    series_id: str = Field(..., description="Parent series id")
    title: str = Field(..., description="Episode title")
    synopsis: Optional[str] = Field(None, description="Short synopsis")
    thumb_url: Optional[str] = Field(None, description="Thumbnail URL")
    video_url: Optional[str] = Field(None, description="Animated comic video URL")
    episode_number: int = Field(..., ge=1, description="Episode order number")
    season: Optional[int] = Field(default=1, ge=1, description="Season number")
    duration_sec: Optional[int] = Field(default=None, ge=0, description="Duration in seconds")
