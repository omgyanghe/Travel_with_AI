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
├
└── README.md
```

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

### LangChain 使用高德地图MCP工具

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

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

```

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
