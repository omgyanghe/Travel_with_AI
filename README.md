# Travel_with_AI（去哪住哪 玩啥吃啥） 🌍✈️

基于LangChain1.x版本框架构建的智能旅行规划助手,集成高德地图MCP服务,提供个性化的旅行计划生成。

## ✨ 功能特点

- 🤖 **AI驱动的旅行规划**: 基于LangChain1.x版本的混合二Agent架构（Orchestrator + Researcher），智能生成详细的多日旅程
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
│   ├── agents/                   # 二Agent 协作系统
│   │   ├── __init__.py
│   │   ├── orchestrator.py       # 总控编排 Agent (大脑，无 MCP 工具)
│   │   ├── researcher.py         # 信息采集 Agent (手脚，拥有全部 MCP 工具)
│   │   ├── prompt_templates.py   # 各 Agent 的 Prompt 模板
│   │   └── base_agent.py         # Agent 基类
│   ├── mcp/                      # MCP 服务集成 (单例模式)
│   │   ├── __init__.py
│   │   ├── client_manager.py     # MCP 客户端管理器 (全局唯一实例)
│   │   └── tools.py              # MCP 工具封装
│   ├── services/                 # 业务服务层
│   │   ├── __init__.py
│   │   ├── research_service.py   # 研究服务 (封装 Researcher Agent 的调用)
│   │   ├── itinerary_assembler.py # 行程组装服务 (格式化输出 + Unsplash 图片)
│   │   └── image_service.py      # 图片搜索服务 (Unsplash)
│   ├── frontend/                 # Gradio 前端
│   │   ├── __init__.py
│   │   ├── app.py                # Gradio 应用入口
│   │   ├── components.py         # UI 组件定义
│   │   └── styles.py             # 样式配置
│   ├── wechat/                   # 微信机器人接口
│   │   ├── __init__.py
│   │   └── bot.py                # WeChat Bot 消息处理
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

本项目采用**混合模式二 Agent 架构**——Orchestrator（大脑，不管工具）+ Researcher（手脚，拥有全部工具），兼顾简洁性和扩展性：

```
用户请求（Gradio / WeChat Bot 共用同一后端）
    ↓
[Orchestrator Agent] ← 总控编排，负责"思考"
    │   无 MCP 工具，专注于策略
    │   1. 解析用户需求（目的地、日期、偏好）
    │   2. 拆分研究任务（分天/分城市）
    │   3. 逐天调用 Researcher 采集数据
    │   4. 汇总所有数据，组装最终行程
    ↓
[Research Service] ← 封装对 Researcher Agent 的调用
    ↓
[Researcher Agent] ← 信息采集，负责"执行"
    │   拥有 ALL MCP 工具
    │   接收具体研究任务（某天、某城市）
    │   被 Prompt 明确引导：多工具调用、全面采集
    │   返回结构化的研究结果
    ↓
[itinerary_assembler] ← 格式化输出，调用 image_service 补充图片
    ↓
用户查看完整旅行计划
```

#### 各组件职责说明

| 组件 | 职责 | MCP 工具 |
|------|------|---------|
| **Orchestrator Agent** | 总控编排：解析用户输入 → 拆分研究任务 → 循环调用 Researcher → 组装输出 | 无 |
| **Researcher Agent** | 信息采集：接收具体任务，使用全部可用 MCP 工具进行多轮搜索和数据采集 | 全部 (`maps_weather`, `maps_text_search`, `maps_around_search`, `maps_search_detail`, `maps_direction_*` 等) |
| **Research Service** | 服务封装：封装对 Researcher Agent 的调用，提供简洁的 `research(task)` 接口 | 无 |
| **Itinerary Assembler** | 行程组装：将研究数据格式化为 Markdown 行程，调用 Unsplash 补充景点图片 | 无 |
| **Image Service** | 图片服务：根据 POI 名称从 Unsplash 搜索相关图片 | 无 |

#### 架构设计决策：为什么从 7 Agent 精简到 2 Agent

| 对比维度 | 原方案 (7 Agent) | 新方案 (2 Agent) |
|---------|-----------------|-----------------|
| Agent 数量 | 7 个（Coordinator + Weather + POI + Route + Accommodation + Dining + Planner） | 2 个（Orchestrator + Researcher） |
| "单工具"问题 | 每个 Agent 只绑 1-2 个工具，天然无法多工具联动 | Researcher 拥有所有工具，Prompt 引导多工具协同 |
| 协调复杂度 | 高（串行/并行调度 5+ 子 Agent） | 低（Orchestrator 顺序调用 Researcher） |
| 代码冗余 | 高（每个 Agent 都要写模板类、Service 包装） | 低（只有两个核心 Agent） |
| 信息连贯性 | 差（天气、POI、路线数据分头返回，上下文割裂） | 好（Researcher 一次性返回某天的完整研究结果） |
| 扩展性 | 每加一个功能要加一个 Agent | 通过在 Prompt 中扩展 Researcher 的能力范围即可 |

#### Agent 交互特点

1. **混合模式**: Orchestrator（中心化控制器）+ Researcher（能力型 Worker），兼顾可控性和灵活性
2. **职责分离**: "想"和"做"分离——Orchestrator 只管策略和编排，Researcher 只管工具调用和数据采集
3. **顺序调用**: Orchestrator 用代码循环逐步调用 Researcher，简单直接，便于调试和错误处理
4. **Prompt 驱动的多工具调用**: Researcher 的 system prompt 明确要求"请使用所有可用的 MCP 工具进行全面的信息采集"，解决单 Agent 只调一个工具的问题
5. **统一后端**: 所有旅行规划逻辑封装在 Agent 层，Gradio 和 WeChat Bot 都通过相同的服务接口调用
6. **MCP 单例模式**: Orchestrator 和 Researcher 共享同一个 MCP 客户端实例，避免多进程资源浪费和 API 速率限制问题

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
│           Researcher Agent                           │
│  - 信息采集 Agent，拥有全部 MCP 工具                  │
│  - 从 Manager 获取共享的 MCP 工具                    │
│  - 被 Orchestrator 通过 Research Service 调用        │
└─────────────────────────────────────────────────────┘
                          ↑ 调用
┌─────────────────────────────────────────────────────┐
│           Orchestrator Agent                         │
│  - 总控编排 Agent，无 MCP 工具                       │
│  - 通过 Research Service 委派研究任务                │
└─────────────────────────────────────────────────────┘
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

### Researcher Agent（信息采集，拥有全部 MCP 工具）

```python
# src/agents/researcher.py
from langchain.agents import create_agent
from src.mcp.client_manager import mcp_manager
from src.agents.prompt_templates import RESEARCHER_SYSTEM_PROMPT

class ResearcherAgent:
    """信息采集 Agent —— 负责调用 MCP 工具进行全面数据采集"""
    
    def __init__(self, llm):
        self.llm = llm
        self._tools = None
        self._agent = None
    
    async def _initialize(self):
        """获取所有 MCP 工具并创建 Agent"""
        if self._agent is None:
            self._tools = await mcp_manager.get_tools()
            self._agent = create_agent(
                self.llm,
                self._tools,
                prompt=RESEARCHER_SYSTEM_PROMPT
            )
    
    async def research(self, task: str) -> str:
        """执行一个具体的研究任务
        
        Args:
            task: 具体的研究指令，如："研究北京第1天的行程：
                  查询天气、搜索景点、推荐酒店和餐厅、规划交通"
        """
        await self._initialize()
        response = await self._agent.ainvoke(
            {"messages": [{"role": "user", "content": task}]}
        )
        return response["messages"][-1].content
```

### Orchestrator Agent（总控编排，无 MCP 工具）

```python
# src/agents/orchestrator.py
from src.services.research_service import ResearchService
from src.services.itinerary_assembler import ItineraryAssembler

class OrchestratorAgent:
    """总控编排 Agent —— 负责"思考"和编排，不直接调用 MCP 工具"""
    
    def __init__(self, llm):
        self.llm = llm
        self.research_service = ResearchService(llm)
        self.assembler = ItineraryAssembler()
    
    async def plan_trip(self, user_request: dict) -> str:
        """规划完整旅行
        
        Args:
            user_request: {destination, days, preferences, ...}
        """
        # 1. 解析用户需求，拆分研究任务
        tasks = self._create_research_tasks(user_request)
        
        # 2. 逐天调用 Researcher 采集数据
        all_research_results = []
        for task in tasks:
            result = await self.research_service.research(task)
            all_research_results.append(result)
        
        # 3. 组装最终行程
        itinerary = await self.assembler.assemble(
            user_request,
            all_research_results
        )
        return itinerary
    
    def _create_research_tasks(self, user_request: dict) -> list[str]:
        """将用户需求拆分为逐天的研究任务"""
        destination = user_request["destination"]
        days = user_request["days"]
        preferences = user_request.get("preferences", "")
        
        tasks = []
        for day in range(1, days + 1):
            task = (
                f"请为{destination}的第{day}天旅行进行全面研究，包括：\n"
                f"1. 使用 maps_weather 查询当天天气\n"
                f"2. 使用 maps_text_search 搜索{day == 1 and '热门' or '适合深度游的'}景点\n"
                f"3. 使用 maps_around_search 搜索景点周边的餐厅和酒店\n"
                f"4. 使用 maps_search_detail 获取主要景点的详细信息\n"
                f"5. 使用 maps_direction_transit_integrated_by_address 规划公共交通路线\n"
                f"用户偏好：{preferences}\n"
                f"请使用所有可用的 MCP 工具进行全面深入的研究。"
            )
            tasks.append(task)
        return tasks
```

### Service 层封装

```python
# src/services/research_service.py
from src.agents.researcher import ResearcherAgent

class ResearchService:
    """研究服务 —— 封装 Researcher Agent 的调用"""
    
    def __init__(self, llm):
        self.researcher = ResearcherAgent(llm)
    
    async def research(self, task: str) -> str:
        """执行研究任务"""
        return await self.researcher.research(task)
```

### 应用初始化（统一后端入口）

```python
# src/frontend/app.py
import asyncio
from src.mcp.client_manager import mcp_manager
from src.agents.orchestrator import OrchestratorAgent

async def initialize_app():
    """应用初始化：创建共享的 MCP 客户端和 Orchestrator"""
    await mcp_manager.get_client()
    # Orchestrator 会通过 ResearchService 自动创建共享 MCP 的 Researcher
    return OrchestratorAgent(llm)

async def shutdown_app():
    """应用关闭：清理 MCP 连接"""
    await mcp_manager.close()

# Gradio 和 WeChat Bot 都通过同一个 orchestrator 调用
# 前端只需: result = await orchestrator.plan_trip(user_request)
```

### 旧方案 vs 新方案对比

| 特性 | 旧方案：每 Agent 一个工具 (❌) | 新方案：2 Agent 混合模式 (✅) |
|------|---------------------------|---------------------------|
| Agent 数量 | 7 个 | 2 个 |
| MCP 进程数 | 1 个（共享） | 1 个（共享） |
| 多工具协同 | 天然不支持 | Prompt 引导，全量工具可用 |
| 代码量 | 高（7 个 Agent 类 + 5 个 Service） | 低（2 个 Agent 类 + 2 个 Service） |
| 调试难度 | 高（需追踪多个 Agent 调用链） | 低（顺序调用，日志清晰） |
| 扩展新功能 | 需添加新 Agent | 修改 Prompt + 拆分新任务类型 |
| 与前端集成 | 每个 Agent 独立暴露 | 统一 `orchestrator.plan_trip()` 接口 |

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
