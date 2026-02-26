from __future__ import annotations

from ..config.constants import API_PREFIX
from ..models.feeds import Comment
from ._base import BaseRestClient


class ReactionsClient(BaseRestClient):
    async def create_comment(self, post_id: str, content: str) -> Comment:
        data = await self._post(
            f"{API_PREFIX}/comments",
            {"postId": post_id, "content": content},
        )
        return Comment.model_validate(data)
