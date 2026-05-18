"""
Gradio 应用入口

职责：
  - 初始化 LLM 和 Orchestrator Agent
  - 创建 Gradio 界面
  - 管理 MCP 客户端的生命周期（启动/关闭）
"""

import asyncio
import gradio as gr

from langchain_openai import ChatOpenAI

from src.mcp.client_manager import mcp_manager
from src.agents.orchestrator import OrchestratorAgent
from src.frontend.components import create_input_panel, create_output_panel
from src.frontend.styles import CUSTOM_CSS
from src.utils.config import config
from src.utils.logger import logger


def create_llm() -> ChatOpenAI:
    """创建 LLM 实例

    支持所有兼容 OpenAI API 的服务（OpenAI / DeepSeek / Qwen 等）
    """
    return ChatOpenAI(
        api_key=config.LLM_API_KEY,
        base_url=config.LLM_BASE_URL,
        model=config.LLM_MODEL_NAME,
        temperature=0.7,  # 适当保留创造性，生成更丰富的旅行建议
    )


async def initialize_app():
    """应用初始化：创建共享的 MCP 客户端和 Orchestrator

    关键设计：
      - MCP 客户端全局共享（单例模式）
      - Orchestrator 内部通过 ResearchService 自动创建共享 MCP 的 Researcher
      - 所有前端（Gradio、WeChat Bot）共用同一个 Orchestrator 实例
    """
    logger.info("=== Travel_with_AI 应用启动中 ===")

    # 验证关键配置
    config.validate()

    # 预初始化 MCP 客户端（首次连接，后续复用）
    await mcp_manager.get_client()

    # 创建 LLM 实例
    llm = create_llm()

    # 创建 Orchestrator（Researcher 通过 ResearchService 内部创建，共享 MCP）
    orchestrator = OrchestratorAgent(llm)

    logger.info("=== 应用初始化完成 ===")
    return orchestrator


async def shutdown_app():
    """应用关闭：清理 MCP 连接"""
    logger.info("=== Travel_with_AI 应用关闭中 ===")
    await mcp_manager.close()
    logger.info("=== 应用已关闭 ===")


async def on_generate_click(
    destination: str,
    days: int,
    preferences: str,
    start_date: str,
) -> str:
    """Gradio "生成旅行计划" 按钮的回调

    这是一个同步、线程安全的包装，确保每次请求都获取到最新的 orchestrator

    Args:
        destination: 目的地城市
        days: 旅行天数
        preferences: 旅行偏好
        start_date: 出发日期

    Returns:
        Markdown 格式的旅行计划
    """
    if not destination.strip():
        return "⚠️ 请输入目的地城市"

    if days < 1 or days > 14:
        return "⚠️ 旅行天数需要在 1-14 天之间"

    # 获取全局 orchestrator（由 Gradio 的 on_startup 创建）
    orchestrator = _get_orchestrator()

    user_request = {
        "destination": destination.strip(),
        "days": days,
        "preferences": preferences.strip(),
        "start_date": start_date.strip(),
    }

    try:
        logger.info(f"收到旅行规划请求: {destination}, {days}天")
        result = await orchestrator.plan_trip(user_request)
        return result
    except Exception as e:
        logger.error(f"旅行规划失败: {e}")
        return f"❌ 生成旅行计划时出错：{str(e)}"


# 全局 orchestrator 引用（由 Gradio 生命周期管理）
_orchestrator: OrchestratorAgent = None


def _get_orchestrator() -> OrchestratorAgent:
    """获取全局 Orchestrator 实例"""
    global _orchestrator
    return _orchestrator


def create_app() -> gr.Blocks:
    """创建 Gradio 应用界面

    Returns:
        配置好的 Gradio Blocks 实例
    """
    global _orchestrator

    with gr.Blocks(
        title="Travel_with_AI - 去哪住哪 玩啥吃啥",
        css=CUSTOM_CSS,
        theme=gr.themes.Soft(primary_hue="emerald"),
    ) as app:
        # 页面标题
        gr.Markdown(
            """
            # 🌍 Travel_with_AI
            ## 去哪住哪 玩啥吃啥 —— AI 驱动的智能旅行规划助手
            """
        )

        # 输入面板
        with gr.Row():
            inputs = create_input_panel()

        # 生成按钮
        generate_btn = gr.Button(
            "🚀 生成旅行计划",
            variant="primary",
            size="lg",
        )

        # 输出面板
        output_md = create_output_panel()

        # 绑定按钮点击事件
        generate_btn.click(
            fn=on_generate_click,
            inputs=[
                inputs["destination"],
                inputs["days"],
                inputs["preferences"],
                inputs["start_date"],
            ],
            outputs=output_md,
        )

    return app


def main():
    """主函数：启动 Gradio 应用

    通过 Gradio 的 on_startup / on_shutdown 管理 MCP 生命周期
    """
    global _orchestrator

    async def startup():
        """Gradio 启动时的初始化"""
        global _orchestrator
        _orchestrator = await initialize_app()

    async def shutdown():
        """Gradio 关闭时的清理"""
        await shutdown_app()

    app = create_app()
    app.on_startup = startup
    app.on_shutdown = shutdown

    logger.info(f"Gradio 应用启动在 http://{config.APP_HOST}:{config.APP_PORT}")
    app.queue()  # 请求排队，避免并发超限
    app.launch(
        server_name=config.APP_HOST,
        server_port=config.APP_PORT,
        share=False,
    )


if __name__ == "__main__":
    main()