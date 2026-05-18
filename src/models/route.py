"""
路线数据模型
表示两点之间的交通路线信息
"""

from dataclasses import dataclass, field


@dataclass
class RouteStep:
    """路线中的单个步骤"""

    instruction: str  # 导航指令描述
    road_name: str = ""  # 道路名称
    distance: str = ""  # 本段距离
    duration: str = ""  # 本段耗时
    transport_mode: str = ""  # 交通方式：walking/driving/transit


@dataclass
class Route:
    """交通路线数据模型"""

    route_id: str = ""
    origin: str = ""  # 起点地址
    destination: str = ""  # 终点地址
    total_distance: str = ""  # 总距离
    total_duration: str = ""  # 总耗时
    transport_mode: str = ""  # 交通方式
    steps: list[RouteStep] = field(default_factory=list)
    cost: str = ""  # 费用估算（公交票价/打车费用）
    polyline: str = ""  # 路线折线坐标（用于地图绘制）