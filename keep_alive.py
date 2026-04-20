import requests
import time
from datetime import datetime

# 你的 Railway 域名
URL = "https://web-production-8483d5.up.railway.app"

def keep_alive():
    try:
        response = requests.get(URL, timeout=30)
        status = "✅ 成功" if response.status_code == 200 else f"⚠️ 状态码: {response.status_code}"
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {status}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ 错误: {e}")

if __name__ == "__main__":
    print("🚀 开始定时访问，保持服务在线...")
    print(f"📍 目标: {URL}")
    print(f"⏰ 间隔: 每 10 分钟\n")

    while True:
        keep_alive()
        time.sleep(600)  # 10 分钟 = 600 秒
