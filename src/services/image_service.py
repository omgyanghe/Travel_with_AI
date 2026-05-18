"""
图片服务 —— 从 Unsplash 搜索景点配图

职责：
  - 根据 POI 名称从 Unsplash API 搜索相关图片
  - 返回可用于 Markdown 的图片 URL
"""

import httpx
from urllib.parse import quote

from src.utils.config import config
from src.utils.logger import logger


class ImageService:
    """图片搜索服务 —— 从 Unsplash 获取景点配图

    设计要点：
      - 可降级：无 Access Key 时返回空列表，不影响主流程
      - 轻量级：不依赖 SDK，直接使用 HTTP API
      - 按需请求：每张图片都是一次独立请求

    使用示例:
        service = ImageService()
        url = await service.search_poi_image("故宫")
    """

    # Unsplash 搜索 API 端点
    UNSPLASH_SEARCH_URL = "https://api.unsplash.com/search/photos"

    def __init__(self):
        """初始化图片服务"""
        self.access_key = config.UNSPLASH_ACCESS_KEY or ""
        if self.access_key:
            logger.info("Unsplash ImageService 已启用")
        else:
            logger.warning("UNSPLASH_ACCESS_KEY 未设置，图片服务将降级为空返回")

    async def search_poi_image(self, poi_name: str) -> str:
        """搜索指定 POI 的首张配图

        Args:
            poi_name: 景点名称，如 "故宫"、"西湖"

        Returns:
            图片 URL 字符串，如果搜索失败或无 Access Key 则返回空字符串
        """
        if not self.access_key:
            return ""

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    self.UNSPLASH_SEARCH_URL,
                    params={
                        "query": f"{poi_name} landmark",
                        "per_page": 1,
                        "orientation": "landscape",
                    },
                    headers={"Authorization": f"Client-ID {self.access_key}"},
                )
                response.raise_for_status()
                data = response.json()
                results = data.get("results", [])
                if results:
                    return results[0]["urls"]["regular"]
                return ""
        except Exception as e:
            logger.warning(f"Unsplash 搜索失败 [{poi_name}]: {e}")
            return ""

    async def search_poi_images(self, poi_name: str, count: int = 3) -> list[str]:
        """搜索指定 POI 的多张配图

        Args:
            poi_name: 景点名称
            count: 需要的图片数量，默认 3 张

        Returns:
            图片 URL 列表
        """
        if not self.access_key:
            return []

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    self.UNSPLASH_SEARCH_URL,
                    params={
                        "query": f"{poi_name} landmark",
                        "per_page": count,
                        "orientation": "landscape",
                    },
                    headers={"Authorization": f"Client-ID {self.access_key}"},
                )
                response.raise_for_status()
                data = response.json()
                return [r["urls"]["regular"] for r in data.get("results", [])]
        except Exception as e:
            logger.warning(f"Unsplash 批量搜索失败 [{poi_name}]: {e}")
            return []