from __future__ import annotations

from ..config.constants import API_PREFIX
from ..models.feeds import CopierInfo
from ._base import BaseRestClient


class PiDataClient(BaseRestClient):
    async def get_copiers_public_info(self, user_id: int) -> CopierInfo:
        data = await self._get(f"{API_PREFIX}/pi-data/copiers/{user_id}")
        return CopierInfo.model_validate(data)
