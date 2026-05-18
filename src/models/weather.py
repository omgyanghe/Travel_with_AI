"""
天气数据模型
表示城市的天气信息
"""

from dataclasses import dataclass


@dataclass
class Weather:
    """天气数据模型"""

    city: str = ""
    date: str = ""
    weather: str = ""  # 天气状况描述，如"晴"、"多云"、"雨"
    temperature: str = ""  # 温度，如 "25℃"
    temperature_range: str = ""  # 温度范围，如 "20℃ ~ 28℃"
    humidity: str = ""  # 湿度
    wind_direction: str = ""  # 风向
    wind_power: str = ""  # 风力
    air_quality: str = ""  # 空气质量
    tips: str = ""  # 出行建议


@dataclass
class WeatherForecast:
    """天气预报（多天）"""

    city: str
    forecasts: list[Weather] = None

    def __post_init__(self):
        if self.forecasts is None:
            self.forecasts = []