"""
研究服务 —— 封装 Researcher Agent 的调用

职责：
  - 充当 Orchestrator 和 Researcher 之间的中间层
  - 提供简洁的 research(task) 接口
  - 未来可在此层增加缓存、重试、结果校验等逻辑
"""

from src.agents.researcher import ResearcherAgent
from src.utils.logger import logger


class ResearchService:
    """研究服务 —— 封装 Researcher Agent 的调用

    设计要点：
      - 服务层抽象：Orchestrator 不直接依赖 ResearcherAgent 类
      - 接口极简：只有一个 research(task) 方法，易于测试和替换
      - 扩展点：可在此层增加缓存（避免重复搜索）、重试机制、结果格式化等
    """

    def __init__(self, llm):
        """初始化研究服务

        Args:
            llm: LangChain 兼容的 LLM 实例
        """
        self.researcher = ResearcherAgent(llm)

    async def research(self, task: str) -> str:
        """执行研究任务

        Args:
            task: 具体的研究指令字符串

        Returns:
            结构化的研究结果文本
        """
        logger.info("ResearchService 收到研究任务")
        return await self.researcher.research(task)