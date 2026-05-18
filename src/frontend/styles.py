"""
Gradio 自定义样式配置
"""

CUSTOM_CSS = """
/* 输出面板样式 */
#output-panel {
    min-height: 400px;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 24px;
    background: #fafafa;
}

#output-panel h1 {
    color: #2d3436;
    border-bottom: 2px solid #00b894;
    padding-bottom: 12px;
    margin-bottom: 20px;
}

#output-panel h2 {
    color: #2d3436;
    margin-top: 28px;
    padding-left: 12px;
    border-left: 4px solid #00b894;
}

#output-panel h3 {
    color: #636e72;
    margin-top: 16px;
}

/* 按钮样式 */
button[variant="primary"] {
    font-size: 18px !important;
    font-weight: 600 !important;
    padding: 12px 32px !important;
    border-radius: 10px !important;
    transition: all 0.3s ease !important;
}

button[variant="primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 184, 148, 0.3);
}

/* 输入组件间距 */
.gradio-container .form {
    gap: 12px;
}
"""