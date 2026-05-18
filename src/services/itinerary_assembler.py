"""
行程组装服务

职责：
  - 将多天的研究结果格式化为结构化的 Markdown 行程
  - 调用 ImageService 为景点补充 Unsplash 配图
"""

from src.services.image_service import ImageService
from src.utils.logger import logger


class ItineraryAssembler:
    """行程组装服务 —— 将原始研究数据格式化为精美的 Markdown 旅行计划

    设计要点：
      - 纯文本处理：不依赖 LLM，直接拼接和格式化
      - 图片增强：为每个景点调用 Unsplash 获取配图
      - Markdown 输出：生成可直接在 Gradio/微信中渲染的 Markdown 文本
    """

    def __init__(self):
        """初始化行程组装服务"""
        self.image_service = ImageService()

    async def assemble(
        self,
        user_request: dict,
        all_research_results: list[str],
    ) -> str:
        """组装完整的旅行计划

        Args:
            user_request: 用户请求字典，包含 destination、days、preferences 等
            all_research_results: 每天的研究结果列表，长度等于天数

        Returns:
            Markdown 格式的完整旅行计划文本
        """
        destination = user_request.get("destination", "未知目的地")
        days = user_request.get("days", len(all_research_results))
        preferences = user_request.get("preferences", "无特殊偏好")
        start_date = user_request.get("start_date", "")

        # 构建旅行计划头部
        md_parts = []
        md_parts.append(f"# 🗺️ {destination}旅行计划\n")
        md_parts.append(f"**旅行天数**：{days} 天\n")
        if start_date:
            md_parts.append(f"**出发日期**：{start_date}\n")
        if preferences:
            md_parts.append(f"**旅行偏好**：{preferences}\n")
        md_parts.append("\n---\n")

        # 逐天处理研究结果
        for day_index, research_result in enumerate(all_research_results):
            day_num = day_index + 1
            md_parts.append(f"## 📅 第 {day_num} 天\n\n")
            # 将 Researcher 返回的原始结果直接嵌入
            md_parts.append(research_result)
            md_parts.append("\n\n---\n")

        # 添加底部说明
        md_parts.append("\n\n> 💡 **提示**：以上行程由 AI 自动生成，建议出发前核实景点开放时间及天气变化。\n")

        return "\n".join(md_parts)

    def format_poi_section(self, pois: list[dict]) -> str:
        """格式化 POI 列表为 Markdown（辅助方法）

        Args:
            pois: POI 字典列表，每个包含 name、address、rating、description 等字段

        Returns:
            格式化后的 Markdown 文本
        """
        lines = []
        for poi in pois:
            name = poi.get("name", "未知")
            address = poi.get("address", "")
            rating = poi.get("rating", "")
            description = poi.get("description", "")

            lines.append(f"### 🏛️ {name}")
            if rating:
                lines.append(f"- ⭐ 评分：{rating}")
            if address:
                lines.append(f"- 📍 地址：{address}")
            if description:
                lines.append(f"- 📝 {description}")
            lines.append("")

        return "\n".join(lines)