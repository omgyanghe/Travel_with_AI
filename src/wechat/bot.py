"""
微信机器人接口

职责：
  - 接收微信公众号/企业微信的消息推送
  - 解析用户的旅行请求
  - 调用 Orchestrator Agent 生成旅行计划
  - 返回格式化结果给用户

设计要点：
  - 与 Gradio 共用同一个 Orchestrator 实例（统一后端）
  - 异步处理：避免长时间等待导致微信服务器超时
"""

import asyncio

from src.agents.orchestrator import OrchestratorAgent
from src.utils.config import config
from src.utils.logger import logger


class WeChatBot:
    """微信机器人 —— 通过企业微信/公众号接收和回复旅行规划请求

    使用示例:
        bot = WeChatBot(orchestrator)
        reply = await bot.process_message("我想去北京玩3天")
    """

    def __init__(self, orchestrator: OrchestratorAgent):
        """初始化微信机器人

        Args:
            orchestrator: 全局共享的 Orchestrator Agent 实例
        """
        self.orchestrator = orchestrator

    async def process_message(self, message: str) -> str:
        """处理用户发送的消息

        当前为简化版实现，仅支持"去 X 玩 N 天"格式的简单解析。
        未来可接入 LLM 做更智能的意图识别和槽位填充。

        Args:
            message: 用户发送的文本消息

        Returns:
            回复消息文本（Markdown 格式的旅行计划）
        """
        logger.info(f"WeChat Bot 收到消息: {message}")

        # 简单解析用户消息（未来可用 LLM 做 NLU）
        user_request = self._parse_message(message)

        if not user_request:
            return (
                "🤔 抱歉，我没能理解你的需求。请尝试以下格式：\n\n"
                "📌 **示例**：\n"
                "- "我想去北京玩3天"\n"
                "- "帮我规划上海2天的行程"\n"
                "- "去成都5天，喜欢美食"\n\n"
                "💡 你也可以在 Web 端使用完整功能：https://...\"
            )

        try:
            itinerary = await self.orchestrator.plan_trip(user_request)
            return itinerary
        except Exception as e:
            logger.error(f"WeChat Bot 处理失败: {e}")
            return f"❌ 生成旅行计划时出现错误，请稍后再试。\n\n错误信息：{str(e)}"

    def _parse_message(self, message: str) -> dict | None:
        """简单规则解析用户消息

        Args:
            message: 用户输入的文本

        Returns:
            解析出的 user_request 字典，解析失败返回 None
        """
        import re

        message = message.strip()

        # 尝试匹配 "去XX玩N天" 或 "XX玩N天" 格式
        pattern = r"(?:去|到)?(.{2,10}?)(?:玩|旅游|旅行|待)(\d+)\s*天"
        match = re.search(pattern, message)

        if not match:
            return None

        destination = match.group(1)
        days = int(match.group(2))

        if days < 1 or days > 14:
            days = min(max(days, 1), 14)

        # 提取偏好关键词
        preferences = ""
        preference_keywords = ["美食", "历史文化", "自然风光", "购物", "亲子", "经济"]
        for kw in preference_keywords:
            if kw in message:
                if preferences:
                    preferences += "、"
                preferences += kw

        return {
            "destination": destination,
            "days": days,
            "preferences": preferences,
        }


async def create_wechat_bot(orchestrator: OrchestratorAgent) -> WeChatBot:
    """创建 WeChat Bot 实例的工厂函数

    Args:
        orchestrator: 全局 Orchestrator 实例

    Returns:
        初始化好的 WeChatBot 实例
    """
    logger.info("WeChat Bot 已创建")
    return WeChatBot(orchestrator)