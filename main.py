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

# 【省錢關鍵】設定通知門檻
# 只有當價格變動 >= 這個數字才通知
NOTIFY_THRESHOLD = 5.0  
# =========================================

def send_line_push(msg):
    line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
    try:
        line_bot_api.push_message(USER_ID, TextSendMessage(text=msg))
        print("✅ 通知已發送")
    except LineBotApiError as e:
        print(f"❌ 發送失敗: {e}")

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
        print(f"抓取失敗: {e}")
        return None

def main():
    current_price = get_current_price()
    if not current_price:
        return

    last_price = 0.0
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                last_price = float(f.read().strip())
            except:
                last_price = 0.0

    print(f"現在價格: {current_price}, 上次價格: {last_price}")

    if last_price != 0:
        # 計算價差絕對值
        diff = current_price - last_price
        abs_diff = abs(diff) # 取絕對值，不管漲跌都算幅度
        
        # 【關鍵判斷】只有當 變動幅度 >= 門檻 時，才發通知
        if abs_diff >= NOTIFY_THRESHOLD:
            icon = "🔺 大漲" if diff > 0 else "🔻 大跌"
            trend = f"+{diff}" if diff > 0 else f"{diff}"
            
            msg = (
                f"{icon} 金價大幅波動！\n"
                f"最新價格: {current_price}\n"
                f"變動幅度: {trend}\n"
                f"(超過設定門檻 {NOTIFY_THRESHOLD} 元)"
            )
            send_line_push(msg)
            
            # 只有發送通知時，才更新紀錄
            # 這樣如果只漲 1 元，下次會繼續累積，直到累積超過 5 元才通知
            with open(HISTORY_FILE, "w") as f:
                f.write(str(current_price))
        else:
            print(f"波動僅 {abs_diff} 元，未達 {NOTIFY_THRESHOLD} 元門檻，不通知。")
            # 注意：這裡不更新檔案，讓微小的漲跌幅可以累積
    else:
        # 第一次執行，直接存檔
        with open(HISTORY_FILE, "w") as f:
            f.write(str(current_price))

if __name__ == "__main__":
    main()
