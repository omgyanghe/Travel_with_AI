import asyncio
import os
from dotenv import load_dotenv

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

# 加载环境变量
load_dotenv()

# Linux/Macos 常见的代理环境变量 的清除，确保国内的测试环境不受代理影响
proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']
for var in proxy_vars:
    if var in os.environ:
        del os.environ[var]

llm_model = ChatOpenAI(
    model=os.getenv("QWEN_LLM_MODEL_ID"),
    temperature=0.7,
    api_key=os.getenv("QWEN_LLM_API_KEY"),
    base_url=os.getenv("QWEN_LLM_BASE_URL"),
)

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
    agent = create_agent(
        llm_model,
        tools  
    )

    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "我想去北京玩两天，预算充足，请你帮我制定一个计划。包括景点、餐厅和酒店的推荐，并且要考虑交通便利性（公共交通）。"}]}
    )

    print(response)

    # print(f"\n✅ 成功获取到 {len(tools)} 个工具：\n")
    
    # 打印工具列表
    # print("可用工具:")
    # for tool in tools:
    #     print(tool)
        # print(f"- {tool.name}")

    # 后续即可将 tools 传入你的 Agent
    # agent = create_react_agent(model, tools)

if __name__ == "__main__":
    asyncio.run(main())