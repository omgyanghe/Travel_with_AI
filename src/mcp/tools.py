"""
MCP 工具封装模块
提供便捷的工具查询和调用辅助函数
"""

from src.mcp.client_manager import mcp_manager
from src.utils.logger import logger


async def get_tool_by_name(name: str):
    """根据工具名称获取单个 MCP 工具

    Args:
        name: 工具名称，如 "maps_weather"、"maps_text_search"

    Returns:
        匹配的工具对象，找不到则返回 None
    """
    tools = await mcp_manager.get_tools()
    for tool in tools:
        if tool.name == name:
            return tool
    logger.warning(f"未找到 MCP 工具: {name}")
    return None


async def list_tool_names() -> list[str]:
    """列出所有可用的 MCP 工具名称

    Returns:
        工具名称列表
    """
    tools = await mcp_manager.get_tools()
    return [tool.name for tool in tools]


async def get_tools_by_category() -> dict[str, list[str]]:
    """按类别分组获取 MCP 工具

    Returns:
        分类后的工具字典，key 为类别名，value 为工具名列表
    """
    tools = await list_tool_names()

    categories = {
        "地理编码": [],
        "天气": [],
        "POI搜索": [],
        "路线规划": [],
        "距离测量": [],
        "其他": [],
    }

    for name in tools:
        if "geo" in name or "regeocode" in name:
            categories["地理编码"].append(name)
        elif "weather" in name:
            categories["天气"].append(name)
        elif "search" in name or "around_search" in name:
            categories["POI搜索"].append(name)
        elif "direction" in name or "bicycling" in name:
            categories["路线规划"].append(name)
        elif "distance" in name:
            categories["距离测量"].append(name)
        else:
            categories["其他"].append(name)

    return categories