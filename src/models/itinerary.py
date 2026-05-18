"""
行程数据模型
定义旅行行程的结构化数据
"""

from datetime import date
from dataclasses import dataclass, field


@dataclass
class DayItinerary:
    """单日行程"""

    day: int
    date: str = ""
    weather: str = ""
    highlights: list[str] = field(default_factory=list)
    morning_activity: str = ""
    afternoon_activity: str = ""
    evening_activity: str = ""
    restaurants: list[str] = field(default_factory=list)
    hotel: str = ""
    transportation: str = ""
    tips: str = ""


@dataclass
class TripItinerary:
    """完整旅行行程"""

    destination: str
    start_date: date
    end_date: date
    total_days: int
    preferences: str = ""
    daily_itineraries: list[DayItinerary] = field(default_factory=list)
    overall_tips: str = ""