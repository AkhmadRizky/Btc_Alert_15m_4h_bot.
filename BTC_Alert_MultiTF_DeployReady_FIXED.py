import time
import requests
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from io import BytesIO
from PIL import Image
import telegram

PAIR = "BTCUSDT"
INTERVALS = ["5m", "15m", "4h"]

# Sudah diisi token & chat_id Bos!
bot = telegram.Bot(token="7966133298:AAHzzZtr_z7qn9OHOovdS4JXUGgFZUPtKEo)
CHAT_ID = "5154881695"

def get_klines(interval, limit=20):
    url = f"https://api.binance.com/api/v3/klines?symbol={PAIR}&interval={interval}&limit={limit}"
    data = requests.get(url).json()
    return [[float(d[1]), float(d[2]), float(d[3]), float(d[4]), int(d[0])] for d in data]

def plot_candles(data, interval):
    fig, ax = plt.subplots()
    for i, (o, h, l, c, _) in enumerate(data):
        color = 'green' if c > o else 'red'
        ax.plot([i, i], [l, h], color='black')
        ax.plot([i, i], [o, c], color=color, linewidth=5)
    ax.set_title(f"{PAIR} ({interval}) Candlestick")
    plt.xticks([])
    plt.yticks([])
    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)
    return buffer

def analyze_trend(data):
    close_prices = [c for _, _, _, c, _ in data]
    ma_short = np.mean(close_prices[-3:])
    ma_long = np.mean(close_prices)
    return "📈 Uptrend" if ma_short > ma_long else "📉 Downtrend"

def send_alert(interval):
    data = get_klines(interval)
    image = plot_candles(data, interval)
    trend = analyze_trend(data)
    price = data[-1][1]
    time_now = datetime.utcnow().strftime('%H:%M:%S UTC')

    message = f"""
📊 BTCUSDT ({interval}) UPDATE

💵 Price: {price}
📈 Trend: {trend}
⏰ Time: {time_now}
"""

    bot.send_photo(chat_id=CHAT_ID, photo=image, caption=message)

if __name__ == "__main__":
    while True:
        for tf in INTERVALS:
            try:
                send_alert(tf)
                time.sleep(5)
            except Exception as e:
                print(f"Error on {tf}: {e}")
        time.sleep(300)  # update setiap 5 menit
