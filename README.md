# Travel_with_AI（去哪住哪 玩啥吃啥） 🌍✈️

基于LangChain1.x版本框架构建的智能旅行规划助手,集成高德地图MCP服务,提供个性化的旅行计划生成。

## ✨ 功能特点

- 🤖 **AI驱动的旅行规划**: 基于LangChain1.x版本框架的多Agents,智能生成详细的多日旅程
- 🗺️ **高德地图集成**: 通过MCP协议接入高德地图服务,支持景点搜索、路线规划、天气查询
- 🧠 **智能工具调用**: Agent自动调用高德地图MCP工具,获取实时POI、路线和天气信息
- 🎨 **现代化前端**: gradio 实现前端构建
- 📱 **完整功能**: 包含住宿、交通、餐饮和景点游览时间推荐

## 🏗️ 技术栈

### 后端
- **框架**: LangChain（1.x版本）
- **MCP工具**: amap-mcp-server (高德地图)，可以在[高德开放平台](https://lbs.amap.com/)注册并获取API密钥。
- **LLM**: 支持多种LLM提供商(OpenAI, DeepSeek，Qwen等)

### 前端
- **框架**: Gradio

## 📁 项目结构

```
Travel_with_AI/
├── src/                          # 源代码目录
│   ├── __init__.py
│   ├── agents/                   # 多 Agent 协作系统
│   │   ├── __init__.py
│   │   ├── coordinator.py        # 总控协调 Agent (Orchestrator)
│   │   ├── travel_planner.py     # 旅行规划 Agent (主策划)
│   │   ├── weather_agent.py      # 天气查询 Agent
│   │   ├── route_agent.py        # 路线规划 Agent
│   │   ├── poi_agent.py          # POI 搜索 Agent
│   │   ├── accommodation_agent.py # 住宿推荐 Agent
│   │   ├── dining_agent.py       # 餐饮推荐 Agent
│   │   ├── prompt_templates.py   # 各 Agent 的 Prompt 模板
│   │   ├── agent_registry.py     # Agent 注册与调度中心
│   │   └── base_agent.py         # Agent 基类 (含 MCP 工具注入)
│   ├── mcp/                      # MCP 服务集成 (单例模式)
│   │   ├── __init__.py
│   │   ├── amap_client.py        # 高德地图 MCP 客户端 (单例)
│   │   ├── client_manager.py     # MCP 客户端管理器 (全局唯一实例)
│   │   └── tools.py              # MCP 工具封装
│   ├── services/                 # 业务服务层 (被 Agents 调用)
│   │   ├── __init__.py
│   │   ├── itinerary_assembler.py # 行程组装服务 (整合各 Agent 输出)
│   │   ├── weather_service.py    # 天气数据服务 (供 WeatherAgent 调用)
│   │   ├── route_service.py      # 路线计算服务 (供 RouteAgent 调用)
│   │   ├── poi_service.py        # POI 搜索服务 (供 POIAgent 调用)
│   │   ├── accommodation_service.py # 住宿推荐服务
│   │   ├── dining_service.py     # 餐饮推荐服务
│   │   └── image_service.py      # 图片搜索服务 (Unsplash，供各 Agent 调用)
│   ├── frontend/                 # Gradio 前端
│   │   ├── __init__.py
│   │   ├── app.py                # Gradio 应用入口
│   │   ├── components.py         # UI 组件定义
│   │   └── styles.py             # 样式配置
│   ├── utils/                    # 工具函数
│   │   ├── __init__.py
│   │   ├── config.py             # 配置管理
│   │   └── logger.py             # 日志配置
│   └── models/                   # 数据模型
│       ├── __init__.py
│       ├── itinerary.py          # 行程数据模型
│       ├── poi.py                # POI 数据模型
│       ├── weather.py            # 天气数据模型
│       └── route.py              # 路线数据模型
├── test/                         # 测试目录
│   ├── __init__.py
│   ├── amap_mcp_test.py          # 高德 MCP 测试
│   ├── llm_test.py               # LLM 连接测试
│   └── agents/                   # Agent 协作测试
│       ├── __init__.py
│       ├── test_weather_agent.py
│       ├── test_route_agent.py
│       └── test_poi_agent.py
├── .env.example                  # 环境变量示例
├── .gitignore                    # Git 忽略配置
├── requirements.txt              # Python 依赖
├── LICENSE                       # 开源许可证
└── README.md                     # 项目说明文档
```

### 🤖 Agent 协作流程

本项目采用**多 Agent 协作架构**，每个 Agent 职责单一、功能专注，通过总控协调 Agent 进行任务分发和结果整合：

```
用户请求
    ↓
[Coordinator Agent] ← 总控协调，解析用户需求，分发任务
    ↓
    ├─→ [Weather Agent] → 调用 weather_service → 返回天气数据
    ├─→ [POI Agent] → 调用 poi_service → 返回景点/酒店/餐厅信息
    ├─→ [Route Agent] → 调用 route_service → 返回路线规划
    ├─→ [Accommodation Agent] → 调用 accommodation_service → 返回住宿推荐
    └─→ [Dining Agent] → 调用 dining_service → 返回餐饮推荐
    ↓
[Travel Planner Agent] ← 汇总所有 Agent 输出，生成完整行程
    ↓
[itinerary_assembler] ← 格式化输出，调用 image_service 补充图片
    ↓
用户查看完整旅行计划
```

#### 各 Agent 职责说明

| Agent | 职责 | 调用的 Service | MCP 工具 |
|-------|------|---------------|---------|
| **Coordinator Agent** | 总控协调，解析用户输入，分发给其他 Agent | 无 | 无 |
| **Weather Agent** | 查询目的地天气信息 | `weather_service` | `maps_weather` |
| **POI Agent** | 搜索景点、酒店、餐厅等 POI 信息 | `poi_service` | `maps_text_search`, `maps_around_search`, `maps_search_detail` |
| **Route Agent** | 规划景点间、酒店到景点等路线 | `route_service` | `maps_direction_*` 系列工具 |
| **Accommodation Agent** | 根据偏好推荐住宿 | `accommodation_service` | `maps_text_search` (搜索酒店) |
| **Dining Agent** | 根据口味和位置推荐餐厅 | `dining_service` | `maps_text_search`, `maps_around_search` |
| **Travel Planner Agent** | 整合所有 Agent 输出，生成结构化行程 | `itinerary_assembler` | 无 (仅协调) |

#### Agent 交互特点

1. **去中心化设计**: 每个 Agent 独立运行，只关注单一功能，便于维护和扩展
2. **服务层抽象**: Agent 不直接调用 MCP 工具，而是通过 Service 层封装，提高可测试性
3. **统一协调**: Coordinator Agent 负责任务编排，避免 Agent 之间的循环依赖
4. **灵活扩展**: 新增功能只需添加新的 Agent 和 Service，不影响现有架构
5. **图片服务共享**: `image_service` 作为共享服务，各 Agent 可在需要时调用获取 POI 图片
6. **MCP 单例模式**: 所有使用高德地图的 Agent 共享同一个 MCP 客户端实例，避免多进程资源浪费和 API 速率限制问题

#### 🔌 MCP 客户端共享机制

为避免多个 Agent 各自创建 MCP 实例导致的资源浪费和 API 限流问题，本项目采用**单例模式**管理 MCP 客户端：

```
┌─────────────────────────────────────────────────────┐
│           MCP Client Manager (单例)                  │
│  - 全局唯一实例                                      │
│  - 负责启动和管理 amap-mcp-server 进程               │
│  - 提供统一的工具访问接口                            │
│  - 集中控制 API 调用频率                             │
└─────────────────────────────────────────────────────┘
                          ↓ 注入
┌─────────────────────────────────────────────────────┐
│              BaseAgent (Agent 基类)                  │
│  - 所有功能 Agent 继承此类                           │
│  - 从 Manager 获取共享的 MCP 工具                     │
│  - 自动注入 weather/route/poi 等工具                 │
└─────────────────────────────────────────────────────┘
                          ↓ 继承
┌──────────┬──────────┬──────────┬──────────┬─────────┐
│ Weather  │  Route   │   POI    │ Accommo- │ Dining  │
│  Agent   │  Agent   │  Agent   │ dation   │  Agent  │
│          │          │          │  Agent   │         │
└──────────┴──────────┴──────────┴──────────┴─────────┘
```

**实现优势：**
- ✅ **节省资源**: 只启动一个 amap-mcp-server 进程，减少内存和 CPU 占用
- ✅ **避免限流**: 统一控制 API 调用频率，防止超过高德 API 速率限制
- ✅ **易于管理**: 集中管理 MCP 连接生命周期，便于错误处理和重试
- ✅ **依赖注入**: 通过基类自动注入工具，Agent 代码更简洁

## 📝 核心功能

1. 在首页填写旅行信息:
   - 目的地城市
   - 旅行日期和天数
   - 交通方式偏好
   - 住宿偏好
   - 旅行风格标签

2. 点击"生成旅行计划"按钮

3. 系统将:
   - 调用Agent生成旅行计划
   - Agent自动调用高德地图MCP工具搜索景点
   - Agent获取天气信息和路线规划
   - 使用 unsplash 完成景点图片搜索
   - 整合所有信息生成完整行程

4. 查看结果:
   - 每日详细行程
   - 景点信息与地图标记
   - 交通路线规划
   - 天气预报
   - 餐饮推荐
   - 景点、美食图片等

## 🔧 核心实现

### MCP 客户端单例模式实现

```python
# src/mcp/client_manager.py
from typing import Optional, Dict, Any
from langchain_mcp_adapters.client import MultiServerMCPClient

class MCPClientManager:
    """MCP 客户端管理器 (单例模式)"""
    
    _instance: Optional['MCPClientManager'] = None
    _client: Optional[MultiServerMCPClient] = None
    
    def __new__(cls) -> 'MCPClientManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def get_client(self) -> MultiServerMCPClient:
        """获取全局唯一的 MCP 客户端实例"""
        if self._client is None:
            # 只在第一次调用时创建新实例
            self._client = MultiServerMCPClient({
                "amap": {
                    "transport": "stdio",
                    "command": "uvx",
                    "args": ["amap-mcp-server"],
                    "env": {"AMAP_MAPS_API_KEY": os.getenv("AMAP_API_KEY")}
                }
            })
            await self._client.__aenter__()
        return self._client
    
    async def get_tools(self) -> Dict[str, Any]:
        """获取所有 MCP 工具"""
        client = await self.get_client()
        return await client.get_tools()
    
    async def close(self):
        """关闭 MCP 客户端连接"""
        if self._client:
            await self._client.__aexit__(None, None, None)
            self._client = None

# 全局管理器实例
mcp_manager = MCPClientManager()
```

### Agent 基类 (自动注入 MCP 工具)

```python
# src/agents/base_agent.py
from langchain.agents import create_agent
from src.mcp.client_manager import mcp_manager

class BaseAgent:
    """所有功能 Agent 的基类，自动注入共享的 MCP 工具"""
    
    def __init__(self, llm, system_prompt: str):
        self.llm = llm
        self.system_prompt = system_prompt
        self._tools = None
    
    async def get_tools(self):
        """从共享的 MCP 管理器获取工具"""
        if self._tools is None:
            self._tools = await mcp_manager.get_tools()
        return self._tools
    
    async def create_agent(self, tools_filter=None):
        """创建 Agent，可选择性地过滤工具"""
        all_tools = await self.get_tools()
        
        # 如果提供了过滤器，只保留指定的工具
        if tools_filter:
            filtered_tools = [t for t in all_tools if tools_filter(t.name)]
        else:
            filtered_tools = all_tools
        
        return create_agent(
            self.llm,
            filtered_tools,
            prompt=self.system_prompt
        )
```

### 功能 Agent 示例 (WeatherAgent)

```python
# src/agents/weather_agent.py
from .base_agent import BaseAgent
from src.agents.prompt_templates import WEATHER_AGENT_PROMPT

class WeatherAgent(BaseAgent):
    """天气查询 Agent"""
    
    def __init__(self, llm):
        super().__init__(llm, WEATHER_AGENT_PROMPT)
    
    async def query_weather(self, city: str):
        """查询指定城市的天气"""
        agent = await self.create_agent(
            tools_filter=lambda name: name == "maps_weather"
        )
        return await agent.ainvoke(f"查询 {city} 的天气")
```

### Service 层使用共享工具

```python
# src/services/weather_service.py
from src.mcp.client_manager import mcp_manager

class WeatherService:
    """天气数据服务 (被 WeatherAgent 调用)"""
    
    def __init__(self):
        self._tools = None
    
    async def get_tools(self):
        if self._tools is None:
            self._tools = await mcp_manager.get_tools()
        return self._tools
    
    async def get_weather(self, city: str) -> dict:
        """获取城市天气信息"""
        tools = await self.get_tools()
        weather_tool = next(t for t in tools if t.name == "maps_weather")
        result = await weather_tool.invoke({"city": city})
        return self._parse_weather_result(result)
```

### 应用启动时的生命周期管理

```python
# src/frontend/app.py
import asyncio
from src.mcp.client_manager import mcp_manager
from src.agents.agent_registry import AgentRegistry

async def initialize_app():
    """应用初始化：创建共享的 MCP 客户端和 Agents"""
    # 预加载 MCP 客户端 (只创建一次)
    await mcp_manager.get_client()
    
    # 创建 Agent 注册中心 (所有 Agent 共享同一个 MCP 实例)
    registry = AgentRegistry()
    await registry.initialize_all_agents()
    
    return registry

async def shutdown_app():
    """应用关闭：清理 MCP 连接"""
    await mcp_manager.close()
```

### LangChain 传统方式 (每个 Agent 独立创建 MCP 实例 - ❌不推荐)

```python
# ❌ 不推荐的做法：每个 Agent 都创建独立的 MCP 客户端
async def create_weather_agent(llm):
    # 问题：每次调用都会启动一个新的 amap-mcp-server 进程
    client = MultiServerMCPClient({
        "amap": {
            "transport": "stdio",
            "command": "uvx",
            "args": ["amap-mcp-server"],
            "env": {"AMAP_MAPS_API_KEY": os.getenv("AMAP_API_KEY")}
        }
    })
    tools = await client.get_tools()
    return create_agent(llm, tools, prompt="...")

# 如果有 5 个 Agent，就会启动 5 个 MCP 服务器进程！
# 导致：资源浪费、API 限流、连接管理复杂
```

### ✅ 推荐做法对比

| 特性 | 传统方式 (❌) | 单例模式 (✅) |
|------|------------|-------------|
| MCP 进程数 | N 个 (N=Agent 数量) | 1 个 (所有 Agent 共享) |
| 内存占用 | 高 (N × 进程开销) | 低 (单一进程) |
| API 限流风险 | 高 (N 倍请求) | 低 (统一控制) |
| 连接管理 | 复杂 (N 个连接) | 简单 (1 个连接) |
| 错误处理 | 分散 | 集中 |
| 代码复用 | 低 | 高 |

### MCP工具调用

Agent可以自动调用以下高德地图MCP工具:
- `maps_text_search`: 搜索景点POI
- `maps_weather`: 查询天气
- `maps_direction_walking_by_address`: 步行路线规划
- `maps_direction_driving_by_address`: 驾车路线规划
- `maps_direction_transit_integrated_by_address`: 公共交通路线规划
- 等等

```text
## amap-mcp-server 可用的工具列表：

### 地理编码工具

#### maps_regeocode
将一个高德经纬度坐标转换为行政区划地址信息

**参数：**
- `location`: 经纬度坐标

#### maps_geo
将详细的结构化地址转换为经纬度坐标。支持对地标性名胜景区、建筑物名称解析为经纬度坐标

**参数：**
- `address`: 结构化地址
- `city` (可选): 指定查询的城市

### 位置服务工具

#### maps_ip_location
IP 定位根据用户输入的 IP 地址，定位 IP 的所在位置

**参数：**
- `ip`: IP地址

#### maps_weather
根据城市名称或者标准adcode查询指定城市的天气

**参数：**
- `city`: 城市名称或者adcode

### 路线规划工具

#### 骑行路线
##### maps_bicycling_by_coordinates
骑行路径规划用于规划骑行通勤方案，规划时会考虑天桥、单行线、封路等情况。最大支持 500km 的骑行路线规划

**参数：**
- `origin`: 起点经纬度坐标
- `destination`: 终点经纬度坐标

##### maps_bicycling_by_address
骑行路径规划（地址版），使用地址进行骑行路线规划，推荐优先使用此工具

**参数：**
- `origin_address`: 起点地址（例如："北京市朝阳区阜通东大街6号"）
- `destination_address`: 终点地址（例如："北京市海淀区上地十街10号"）
- `origin_city` (可选): 起点所在城市，用于提高地理编码准确性
- `destination_city` (可选): 终点所在城市，用于提高地理编码准确性

#### 步行路线
##### maps_direction_walking_by_coordinates
步行路径规划 API 可以根据输入起点终点经纬度坐标规划100km 以内的步行通勤方案，并且返回通勤方案的数据

**参数：**
- `origin`: 起点经纬度坐标
- `destination`: 终点经纬度坐标

##### maps_direction_walking_by_address
步行路径规划（地址版），使用地址进行步行路线规划，推荐优先使用此工具

**参数：**
- `origin_address`: 起点地址（例如："北京市朝阳区阜通东大街6号"）
- `destination_address`: 终点地址（例如："北京市海淀区上地十街10号"）
- `origin_city` (可选): 起点所在城市，用于提高地理编码准确性
- `destination_city` (可选): 终点所在城市，用于提高地理编码准确性

#### 驾车路线
##### maps_direction_driving_by_coordinates
驾车路径规划 API 可以根据用户起终点经纬度坐标规划以小客车、轿车通勤出行的方案，并且返回通勤方案的数据

**参数：**
- `origin`: 起点经纬度坐标
- `destination`: 终点经纬度坐标

##### maps_direction_driving_by_address
驾车路径规划（地址版），使用地址进行驾车路线规划，推荐优先使用此工具

**参数：**
- `origin_address`: 起点地址（例如："北京市朝阳区阜通东大街6号"）
- `destination_address`: 终点地址（例如："北京市海淀区上地十街10号"）
- `origin_city` (可选): 起点所在城市，用于提高地理编码准确性
- `destination_city` (可选): 终点所在城市，用于提高地理编码准确性

#### 公共交通路线
##### maps_direction_transit_integrated_by_coordinates
根据用户起终点经纬度坐标规划综合各类公共（火车、公交、地铁）交通方式的通勤方案，并且返回通勤方案的数据，跨城场景下必须传起点城市与终点城市

**参数：**
- `origin`: 起点经纬度坐标
- `destination`: 终点经纬度坐标
- `city`: 起点城市
- `cityd`: 终点城市

##### maps_direction_transit_integrated_by_address
公共交通路径规划（地址版），使用地址进行公共交通路线规划，推荐优先使用此工具

**参数：**
- `origin_address`: 起点地址（例如："北京市朝阳区阜通东大街6号"）
- `destination_address`: 终点地址（例如："北京市海淀区上地十街10号"）
- `origin_city`: 起点所在城市（跨城交通必需）
- `destination_city`: 终点所在城市（跨城交通必需）

### 距离测量工具

#### maps_distance
测量两个经纬度坐标之间的距离,支持驾车、步行以及球面距离测量

**参数：**
- `origins`: 起点经纬度坐标
- `destination`: 终点经纬度坐标
- `type` (可选，默认为"1"): 测量类型

### POI搜索工具

#### maps_text_search
关键词搜索 API 根据用户输入的关键字进行 POI 搜索，并返回相关的信息

**参数：**
- `keywords`: 搜索关键词
- `city` (可选): 查询城市
- `citylimit` (可选，默认为"false"): 是否限制城市范围内搜索

#### maps_around_search
周边搜，根据用户传入关键词以及坐标location，搜索出radius半径范围的POI

**参数：**
- `location`: 中心点经纬度坐标
- `radius` (可选，默认为"1000"): 搜索半径
- `keywords` (可选): 搜索关键词

#### maps_search_detail
查询关键词搜或者周边搜获取到的POI ID的详细信息

**参数：**
- `id`: POI ID
```
