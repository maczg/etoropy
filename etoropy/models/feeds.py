from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CreatePostRequest(BaseModel):
    content: str
    instrument_id: int | None = Field(None, alias="instrumentId", serialization_alias="instrumentId")


class FeedPost(BaseModel):
    model_config = {"extra": "allow"}

    post_id: str = Field(alias="postId")
    user_id: int = Field(alias="userId")
    username: str
    content: str
    created_at: str = Field(alias="createdAt")
    instrument_id: int | None = Field(None, alias="instrumentId")
    likes_count: int = Field(0, alias="likesCount")
    comments_count: int = Field(0, alias="commentsCount")


class FeedResponse(BaseModel):
    posts: list[FeedPost] = []


class GetFeedParams(BaseModel):
    page: int | None = None
    page_size: int | None = None


class CreateCommentRequest(BaseModel):
    post_id: str = Field(alias="postId", serialization_alias="postId")
    content: str


class Comment(BaseModel):
    model_config = {"extra": "allow"}

    comment_id: str = Field(alias="commentId")
    post_id: str = Field(alias="postId")
    user_id: int = Field(alias="userId")
    username: str
    content: str
    created_at: str = Field(alias="createdAt")


class UserSearchParams(BaseModel):
    search_text: str | None = None
    page: int | None = None
    page_size: int | None = None


class UserProfile(BaseModel):
    model_config = {"extra": "allow"}

    user_id: int = Field(alias="userId")
    username: str
    display_name: str = Field("", alias="displayName")


class UserPerformance(BaseModel):
    model_config = {"extra": "allow"}

    user_id: int = Field(alias="userId")


class UserPortfolio(BaseModel):
    model_config = {"extra": "allow"}

    user_id: int = Field(alias="userId")
    positions: list[Any] = []


class CopierInfo(BaseModel):
    model_config = {"extra": "allow"}

    user_id: int = Field(alias="userId")
    copiers_count: int = Field(0, alias="copiersCount")


class CuratedList(BaseModel):
    model_config = {"extra": "allow"}

    list_id: int = Field(alias="listId")
    name: str
    items: list[Any] = []


class MarketRecommendation(BaseModel):
    model_config = {"extra": "allow"}

    instrument_id: int = Field(alias="instrumentId")
