"""
Researcher Agent（信息采集 Agent）

职责：拥有全部 MCP 工具的 Agent，负责具体的旅行信息采集
- 天气查询
- 景点/餐厅/酒店 POI 搜索
- 路线规划
- 地理编码

被 ResearchService 封装调用，不直接暴露给前端。
"""

from langchain.agents import create_agent

from src.mcp.client_manager import mcp_manager
from src.agents.prompt_templates import RESEARCHER_SYSTEM_PROMPT
from src.utils.logger import logger


class ResearcherAgent:
    """信息采集 Agent —— 负责调用 MCP 工具进行全面数据采集

    设计要点：
      - 拥有全部 MCP 工具（单 Agent 多工具，解决"单工具"问题）
      - Prompt 明确引导：要求使用所有可用工具进行多轮、全面的信息采集
      - 惰性初始化：首次 research() 调用时才创建 Agent，避免空转

    使用示例:
        researcher = ResearcherAgent(llm)
        result = await researcher.research("研究北京第1天的行程...")
    """

    def __init__(self, llm):
        """初始化 Researcher Agent

        Args:
            llm: LangChain 兼容的 LLM 实例（如 ChatOpenAI）
        """
        self.llm = llm
        self._tools = None
        self._agent = None

    async def _initialize(self):
        """惰性初始化：获取 MCP 工具并创建 Agent

        只在首次调用 research() 时执行，避免在不需要时浪费资源
        """
        if self._agent is None:
            logger.info("正在初始化 Researcher Agent...")
            # 从共享的 MCP 管理器获取全部工具（自动包含并发限流）
            self._tools = await mcp_manager.get_tools()
            logger.info(f"Researcher Agent 已加载 {len(self._tools)} 个 MCP 工具")

            # 使用全部工具创建 Agent
            self._agent = create_agent(
                self.llm,
                self._tools,
                prompt=RESEARCHER_SYSTEM_PROMPT,
            )
            logger.info("Researcher Agent 初始化完成")

    async def research(self, task: str) -> str:
        """执行一个具体的研究任务

        Args:
            task: 具体的研究指令，例如：
                  "请为北京的第1天旅行进行全面研究，包括：\n"
                  "1. 使用 maps_weather 查询当天天气\n"
                  "2. 使用 maps_text_search 搜索热门景点\n"
                  "..."

        Returns:
            结构化的研究结果文本，由 LLM 根据工具调用结果整理
        """
        await self._initialize()
        logger.info(f"Researcher 开始执行研究任务...")

        response = await self._agent.ainvoke(
            {"messages": [{"role": "user", "content": task}]}
        )
        result = response["messages"][-1].content
        logger.info(f"Researcher 研究任务完成（结果长度: {len(result)} 字符）")
        return result