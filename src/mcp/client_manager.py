"""
MCP 客户端管理器（单例模式 + 并发限流）

功能：
  1. 单例模式 —— 全局唯一 MCP 客户端实例，避免多进程资源浪费
  2. 并发限流 —— asyncio.Semaphore(3) 限制高德 MCP API 的并发请求数
  3. 工具封装 —— 自动为所有 MCP 工具的 ainvoke 包装限流逻辑
"""

import asyncio
import os
from typing import Optional

from langchain_mcp_adapters.client import MultiServerMCPClient

from src.utils.config import config
from src.utils.logger import logger


class MCPClientManager:
    """MCP 客户端管理器（单例模式 + 并发限流）

    使用示例:
        manager = MCPClientManager()
        client = await manager.get_client()
        tools = await manager.get_tools()
    """

    _instance: Optional["MCPClientManager"] = None
    _client: Optional[MultiServerMCPClient] = None
    _semaphore: Optional[asyncio.Semaphore] = None

    def __new__(cls) -> "MCPClientManager":
        """单例模式：确保全局只有一个管理器实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def semaphore(self) -> asyncio.Semaphore:
        """获取并发信号量（线程安全，单例下只创建一次）

        高德 MCP API 的并发上限为 3 个，超过上限的请求会在此排队等待
        """
        if self._semaphore is None:
            max_concurrent = config.MCP_MAX_CONCURRENT
            self._semaphore = asyncio.Semaphore(max_concurrent)
            logger.info(f"MCP 并发限流已启用: max_concurrent={max_concurrent}")
        return self._semaphore

    async def get_client(self) -> MultiServerMCPClient:
        """获取全局唯一的 MCP 客户端实例

        首次调用时创建连接，后续调用复用已有连接
        """
        if self._client is None:
            logger.info("正在初始化 MCP 客户端...")
            self._client = MultiServerMCPClient({
                "amap": {
                    "transport": "stdio",
                    "command": "uvx",
                    "args": ["amap-mcp-server"],
                    "env": {"AMAP_MAPS_API_KEY": config.AMAP_API_KEY},
                }
            })
            await self._client.__aenter__()
            logger.info("MCP 客户端初始化完成")
        return self._client

    async def get_tools(self):
        """获取所有 MCP 工具（自动包装并发限流）

        返回的工具列表中，每个工具的 ainvoke 方法都经过了信号量包装，
        确保总并发数不超过 MCP_MAX_CONCURRENT 的限制
        """
        client = await self.get_client()
        raw_tools = await client.get_tools()
        logger.info(f"已加载 {len(raw_tools)} 个 MCP 工具")
        return self._wrap_tools_with_rate_limit(raw_tools)

    def _wrap_tools_with_rate_limit(self, tools):
        """为每个工具的 ainvoke 方法包装并发信号量

        原理：
          捕获原始 ainvoke 方法 → 用 async with semaphore 包裹 → 设置新 ainvoke
          这样所有通过 tool.ainvoke() 发起的调用都会自动排队限流
        """
        for tool in tools:
            original_ainvoke = tool.ainvoke

            async def rate_limited_ainvoke(input_data, _orig=original_ainvoke):
                async with self.semaphore:
                    return await _orig(input_data)

            tool.ainvoke = rate_limited_ainvoke

        return tools

    async def close(self):
        """关闭 MCP 客户端连接，释放资源"""
        if self._client:
            logger.info("正在关闭 MCP 客户端...")
            await self._client.__aexit__(None, None, None)
            self._client = None
            logger.info("MCP 客户端已关闭")


# 全局单例实例，所有模块通过此实例访问 MCP 功能
mcp_manager = MCPClientManager()