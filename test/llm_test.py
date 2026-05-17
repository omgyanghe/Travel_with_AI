import asyncio
import os
from dotenv import load_dotenv

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

# 简单的对话
response = llm_model.invoke(
    [
        {"role": "user", "content": "介绍一下你自己"}
    ]
)

print(response.content)