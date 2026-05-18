import asyncio
from wechatbot import WeChatBot

# 创建机器人实例
bot = WeChatBot(
    # 可选配置（推荐加上）
    cred_path="~/.wechatbot/credentials.json",   # 自动保存登录凭证，下次不用重复扫码
    on_qr_url=lambda url: print(f"\n📱 请用微信扫码登录：{url}\n"),
    on_scanned=lambda: print("✅ 已扫码，请在手机上确认登录..."),
    on_error=lambda err: print(f"❌ 错误: {err}"),
)

# 消息处理器（最核心部分）
@bot.on_message
async def handle_message(msg):
    # 打印收到什么消息（调试用）
    print(f"[{msg.type}] {msg.user_id}: {msg.text or '非文本消息'}")
    
    # 如果是文本消息，就回复
    if msg.text:
        await bot.send_typing(msg.user_id)        # 显示“正在输入...”
        await asyncio.sleep(0.01)                  # 模拟思考时间（可选）
        
        reply_text = f"Echo: {msg.text}\n\n—— 来自 WeChatBot Python SDK"
        await bot.reply(msg, reply_text)          # 智能回复（推荐方式）

# 启动机器人
if __name__ == "__main__":
    print("🚀 WeChatBot 正在启动...")
    bot.run()          # 自动处理登录 + 启动监听