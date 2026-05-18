"""
Gradio UI 组件定义
定义输入面板和输出面板的组件布局
"""

import gradio as gr


def create_input_panel() -> dict[str, gr.components.Component]:
    """创建输入面板组件

    Returns:
        组件字典，key 为字段名，value 为 Gradio 组件
    """
    with gr.Column(scale=1):
        destination = gr.Textbox(
            label="📍 目的地城市",
            placeholder="例如：北京、上海、成都...",
            info="输入你要去的城市名称",
        )

        with gr.Row():
            days = gr.Slider(
                label="📅 旅行天数",
                minimum=1,
                maximum=14,
                value=3,
                step=1,
                info="选择旅行天数（1-14天）",
            )
            start_date = gr.Textbox(
                label="🕐 出发日期（可选）",
                placeholder="例如：2025-05-01",
                info="留空则不指定日期",
            )

        preferences = gr.Textbox(
            label="🎯 旅行偏好",
            placeholder="例如：喜欢历史文化，对美食非常感兴趣，希望多安排博物馆",
            info="描述你的旅行偏好，AI 会据此优化行程",
            lines=3,
        )

    return {
        "destination": destination,
        "days": days,
        "preferences": preferences,
        "start_date": start_date,
    }


def create_output_panel() -> gr.Markdown:
    """创建输出面板组件

    Returns:
        用于显示生成结果的 Markdown 组件
    """
    with gr.Column(scale=2):
        output = gr.Markdown(
            value="### 📋 你的旅行计划将在这里显示\n\n点击 **🚀 生成旅行计划** 按钮开始规划...",
            label="旅行计划",
            elem_id="output-panel",
            latex_delimiters=[
                {"left": "$$", "right": "$$", "display": True},
            ],
        )

    return output