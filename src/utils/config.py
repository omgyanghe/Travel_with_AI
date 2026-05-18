"""
配置管理模块
从环境变量加载所有应用配置，提供统一的配置访问接口
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()


class Config:
    """应用全局配置（单例模式，所有配置从环境变量读取）"""

    # ===== LLM 配置 =====
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "gpt-4o")

    # ===== 高德地图配置 =====
    AMAP_API_KEY: str = os.getenv("AMAP_API_KEY", "")

    # ===== Unsplash 配置 =====
    UNSPLASH_ACCESS_KEY: str = os.getenv("UNSPLASH_ACCESS_KEY", "")

    # ===== 微信机器人配置 =====
    WECHAT_TOKEN: str = os.getenv("WECHAT_TOKEN", "")

    # ===== MCP 并发控制 =====
    # 高德 MCP API 的最大并发请求数
    MCP_MAX_CONCURRENT: int = int(os.getenv("MCP_MAX_CONCURRENT", "3"))

    # ===== 应用配置 =====
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "7860"))

    @classmethod
    def validate(cls) -> bool:
        """验证关键配置是否已设置"""
        if not cls.LLM_API_KEY:
            raise ValueError("LLM_API_KEY 未设置，请在 .env 文件中配置")
        if not cls.AMAP_API_KEY:
            raise ValueError("AMAP_API_KEY 未设置，请在 .env 文件中配置")
        return True


# 全局配置实例
config = Config()