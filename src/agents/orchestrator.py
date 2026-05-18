"""
Orchestrator Agent（总控编排 Agent）

职责：负责"思考"和编排，不直接调用 MCP 工具
  1. 解析用户需求 → 拆分研究任务
  2. 逐天调用 ResearchService → 委托 Researcher 采集数据
  3. 汇总结果 → 调用 ItineraryAssembler 组装最终行程

设计原则：
  - "想"和"做"分离：Orchestrator 只管策略，Researcher 只管执行
  - 顺序调用：简单直接的循环调用，便于调试和错误处理
  - 统一后端：Gradio 和 WeChat Bot 都通过 Orchestrator.plan_trip() 调用
"""

from src.services.research_service import ResearchService
from src.services.itinerary_assembler import ItineraryAssembler
from src.utils.logger import logger


class OrchestratorAgent:
    """总控编排 Agent —— 负责"思考"和编排，不直接调用 MCP 工具

    使用示例:
        orchestrator = OrchestratorAgent(llm)
        itinerary = await orchestrator.plan_trip({
            "destination": "北京",
            "days": 3,
            "preferences": "喜欢历史文化，美食优先"
        })
    """

    def __init__(self, llm):
        """初始化 Orchestrator Agent

        Args:
            llm: LangChain 兼容的 LLM 实例
        """
        self.llm = llm
        # ResearchService 内部创建 ResearcherAgent，共享同一个 LLM
        self.research_service = ResearchService(llm)
        # ItineraryAssembler 负责将研究数据格式化为最终行程
        self.assembler = ItineraryAssembler()

    async def plan_trip(self, user_request: dict) -> str:
        """规划完整旅行计划（统一后端入口）

        流程：
          1. 解析用户需求 → 拆分为按天的研究任务
          2. 逐天调用 Researcher 采集数据（顺序执行，方便调试）
          3. 将所有研究结果交给 ItineraryAssembler 组装输出

        Args:
            user_request: 用户请求字典，包含以下字段：
                - destination (str): 目的地城市，如 "北京"
                - days (int): 旅行天数
                - preferences (str, optional): 旅行偏好，如 "喜欢美食、历史文化"
                - start_date (str, optional): 出发日期

        Returns:
            Markdown 格式的完整旅行计划
        """
        destination = user_request.get("destination", "")
        days = user_request.get("days", 1)

        logger.info(f"Orchestrator 开始规划旅行: 目的地={destination}, 天数={days}")

        # 第一步：拆分研究任务
        tasks = self._create_research_tasks(user_request)
        logger.info(f"已拆分 {len(tasks)} 个研究任务")

        # 第二步：逐天调用 Researcher 采集数据
        all_research_results = []
        for idx, task in enumerate(tasks):
            logger.info(f"正在执行第 {idx + 1}/{len(tasks)} 个研究任务...")
            result = await self.research_service.research(task)
            all_research_results.append(result)
            logger.info(f"第 {idx + 1} 个研究任务完成")

        # 第三步：组装最终行程
        logger.info("正在组装最终行程...")
        itinerary = await self.assembler.assemble(
            user_request,
            all_research_results,
        )
        logger.info("旅行计划生成完成")
        return itinerary

    def _create_research_tasks(self, user_request: dict) -> list[str]:
        """将用户需求拆分为按天的研究任务

        每天的任务包含：天气查询 → 景点搜索 → 周边餐饮 → 酒店推荐 → 交通规划

        第一天和后续几天的侧重点不同：
          - 第一天：侧重热门景点，帮助用户快速融入
          - 后续天：侧重深度游景点，提供更丰富的体验

        Args:
            user_request: 用户请求字典

        Returns:
            研究任务指令列表，每个元素对应一天的研究任务
        """
        destination = user_request.get("destination", "")
        days = user_request.get("days", 1)
        preferences = user_request.get("preferences", "")

        tasks = []
        for day in range(1, days + 1):
            # 第一天搜"热门景点"，后续搜"深度游"景点
            attraction_keyword = "热门" if day == 1 else "适合深度游的"

            # 根据偏好调整餐饮关键词
            if "美食" in preferences:
                dining_keyword = "当地特色美食餐厅"
            elif "经济" in preferences:
                dining_keyword = "性价比高的餐厅"
            else:
                dining_keyword = "推荐餐厅"

            task = (
                f"请为{destination}的第{day}天旅行进行全面研究，包括：\n"
                f"1. 使用 maps_weather 查询当天天气\n"
                f"2. 使用 maps_text_search 搜索{attraction_keyword}景点\n"
                f"3. 使用 maps_around_search 搜索景点周边的{dining_keyword}和酒店\n"
                f"4. 使用 maps_search_detail 获取主要景点的详细信息\n"
                f"5. 使用 maps_direction_transit_integrated_by_address 规划公共交通路线\n"
                f"用户偏好：{preferences}\n"
                f"请使用所有可用的 MCP 工具进行全面深入的研究。"
            )
            tasks.append(task)

        return tasks