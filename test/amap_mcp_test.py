import asyncio
import os
from dotenv import load_dotenv

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

# 加载环境变量
load_dotenv()

async def main():
    # 使用 uvx 启动 MCP 服务器
    client = MultiServerMCPClient(
        {
            "amap": {
                "transport": "stdio",
                "command": "uvx",
                "args": ["amap-mcp-server"],
                "env": {"AMAP_MAPS_API_KEY": os.getenv("AMAP_API_KEY")}
            }
        }
    )

    # 连接并获取工具
    tools = await client.get_tools()

    print(f"\n✅ 成功获取到 {len(tools)} 个工具：\n")
    
    # 打印工具列表
    print("可用工具:")
    for tool in tools:
        print(f"- {tool.name}")

    # 后续即可将 tools 传入你的 Agent
    # agent = create_react_agent(model, tools)

if __name__ == "__main__":
    asyncio.run(main())