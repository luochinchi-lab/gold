import requests
from bs4 import BeautifulSoup
import os
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

# ================= 設定區 =================
CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
USER_ID = os.environ.get("USER_ID")
HISTORY_FILE = "last_price.txt"
# =========================================

def send_line_push(msg):
    # 這裡加強了錯誤檢查
    if not CHANNEL_ACCESS_TOKEN:
        print("❌ 錯誤：GitHub Secrets 裡找不到 CHANNEL_ACCESS_TOKEN")
        return
    if not USER_ID:
        print("❌ 錯誤：GitHub Secrets 裡找不到 USER_ID")
        return

    print(f"嘗試發送訊息給 User ID: {USER_ID[:5]}...") # 只印出前5碼確認

    line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
    try:
        line_bot_api.push_message(USER_ID, TextSendMessage(text=msg))
        print("✅ Line 通知發送成功！如果沒收到，請檢查是否已封鎖機器人。")
    except LineBotApiError as e:
        print(f"❌ 發送失敗，Line 回傳錯誤碼: {e.status_code}")
        print(f"錯誤詳情: {e.error.message}")
        print("檢查重點：\n1. Token 是否過期或貼錯？\n2. User ID 是否填成 Line ID (這是不對的)？")

def get_current_price():
    try:
        url = "https://rate.bot.com.tw/gold?Lang=zh-TW"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        row = soup.find('tbody').find_all('tr')[0]
        cells = row.find_all('td')
        return float(cells[3].text.strip().replace(',', ''))
    except Exception as e:
        print(f"抓取錯誤: {e}")
        return None

def main():
    print("--- 啟動強制測試模式 ---")
    
    # 【測試區】不管價格如何，先發一則測試訊息
    test_msg = "🔔 這是測試訊息！\n如果看到這個，代表你的機器人設定完全正確。"
    send_line_push(test_msg)
    # -------------------------------------

    current_price = get_current_price()
    if current_price:
        print(f"目前抓取到的金價: {current_price}")
        
        # 為了測試，強制把價格寫入，不論是否有變動
        with open(HISTORY_FILE, "w") as f:
            f.write(str(current_price))

if __name__ == "__main__":
    main()
