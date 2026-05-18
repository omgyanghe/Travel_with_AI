"""
POI（兴趣点）数据模型
表示地图上的景点、餐厅、酒店等位置信息
"""

from dataclasses import dataclass, field


@dataclass
class POI:
    """POI 数据模型"""

    poi_id: str = ""
    name: str = ""
    address: str = ""
    city: str = ""
    location: str = ""  # 经纬度，格式: "经度,纬度"
    category: str = ""  # 景点/餐厅/酒店等
    rating: str = ""
    phone: str = ""
    photos: list[str] = field(default_factory=list)
    description: str = ""
    open_time: str = ""
    price_range: str = ""


@dataclass
class POISearchResult:
    """POI 搜索结果"""

    keyword: str
    city: str = ""
    results: list[POI] = field(default_factory=list)
    total_count: int = 0