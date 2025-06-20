
import os, time, requests
from binance.client import Client
from telegram import Bot
from PIL import Image
from io import BytesIO

BIN_API = Client(os.getenv("BINANCE_APIKEY"), os.getenv("BINANCE_SECRET"))
TG_BOT = Bot(token=os.getenv("BOT_TOKEN"))
CHAT = os.getenv("CHAT_ID")
PAIR = os.getenv("PAIR", "BTCUSDT")
LOW = float(os.getenv("ALERT_LEVEL_LOW", "102500"))
HIGH = float(os.getenv("ALERT_LEVEL_HIGH", "104200"))

def fetch_klines(interval="15m", limit=50):
    data = BIN_API.get_klines(symbol=PAIR, interval=interval, limit=limit)
    return [{"open":float(d[1]),"close":float(d[4])} for d in data]

def check_signal():
    klines = fetch_klines()
    last = klines[-1]
    prev = klines[-2]
    sig = None
    if last["close"] > HIGH: sig = "🚀 BREAKOUT 15m"
    elif last["close"] < LOW: sig = "📉 BREAKDOWN 15m"
    elif last["open"] < last["close"] and prev["open"] > prev["close"]:
        sig = "🟢 Bullish Reversal 15m"
    elif last["open"] > last["close"] and prev["open"] < prev["close"]:
        sig = "🔴 Bearish Reversal 15m"
    return sig

def screenshot():
    url = f"https://chart-img.com/chart?symbol={PAIR}&interval=15m&theme=dark"
    resp = requests.get(url)
    return resp.content

def send_alert(sig):
    img = screenshot()
    TG_BOT.send_message(CHAT, f"{sig} pada {PAIR}", parse_mode="HTML")
    TG_BOT.send_photo(CHAT, photo=BytesIO(img))

if __name__ == "__main__":
    while True:
        sig = check_signal()
        if sig:
            send_alert(sig)
        time.sleep(60)
