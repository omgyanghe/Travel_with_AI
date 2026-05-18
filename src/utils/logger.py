"""
日志配置模块
提供统一的日志格式和输出配置
"""

import logging
import sys


def setup_logger(name: str = "Travel_with_AI", level: int = logging.INFO) -> logging.Logger:
    """创建并配置应用日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别，默认为 INFO

    Returns:
        配置好的 Logger 实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 控制台输出 handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # 日志格式：时间 - 名称 - 级别 - 消息
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


# 全局默认日志记录器
logger = setup_logger()