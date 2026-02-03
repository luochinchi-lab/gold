import requests
from bs4 import BeautifulSoup
import os
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

# ================= 設定區 =================
# 從 GitHub Secrets 讀取變數
CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
USER_ID = os.environ.get("USER_ID")
HISTORY_FILE = "last_price.txt"
# =========================================

def send_line_push(msg):
    if not CHANNEL_ACCESS_TOKEN or not USER_ID:
        print("錯誤：未設定 Token 或 User ID")
        return

    # 初始化 Line Bot API
    line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
    
    try:
        # 使用 push_message 主動推播
        line_bot_api.push_message(USER_ID, TextSendMessage(text=msg))
        print("Line Bot 通知發送成功")
    except LineBotApiError as e:
        print(f"發送失敗: {e}")

def get_current_price():
    try:
        url = "https://rate.bot.com.tw/gold?Lang=zh-TW"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        row = soup.find('tbody').find_all('tr')[0]
        cells = row.find_all('td')
        # 本行賣出價格
        return float(cells[3].text.strip().replace(',', ''))
    except Exception as e:
        print(f"抓取錯誤: {e}")
        return None

def main():
    print("--- 開始執行價格檢查 (Bot 版) ---")
    current_price = get_current_price()
    
    if not current_price:
        print("無法取得價格，結束。")
        return

    # 讀取上次的價格
    last_price = 0.0
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                content = f.read().strip()
                if content:
                    last_price = float(content)
            except:
                pass

    print(f"目前價格: {current_price}, 上次價格: {last_price}")

    # 比對價格
    if last_price != 0 and current_price != last_price:
        diff = current_price - last_price
        icon = "🔺 漲" if diff > 0 else "🔻 跌"
        trend = f"+{diff}" if diff > 0 else f"{diff}"
        
        msg = (
            f"{icon} 金價變動通知\n"
            f"最新: {current_price}\n"
            f"幅度: {trend}\n"
            f"(前次: {last_price})"
        )
        send_line_push(msg)
    else:
        print("價格無變動或為首次執行")

    # 存檔
    with open(HISTORY_FILE, "w") as f:
        f.write(str(current_price))

if __name__ == "__main__":
    main()
