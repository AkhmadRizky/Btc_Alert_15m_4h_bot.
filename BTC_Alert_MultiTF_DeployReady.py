
import time
import requests
import matplotlib.pyplot as plt
from io import BytesIO
import telegram
from datetime import datetime
import threading

bot = telegram.Bot(token="7966133298:AAHzzZtr_z7qn9OHOovdS4JXUGgFZUPtKEo")
PAIR = "BTCUSDT"
CHAT_ID = 5154881695

def fetch_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    return float(requests.get(url).json()["price"])

def generate_chart(prices, interval):
    plt.figure(figsize=(6, 3))
    plt.plot(prices, marker='o')
    plt.title(f'{PAIR} - {interval} Update')
    plt.xlabel('Update')
    plt.ylabel('Price')
    plt.grid(True)
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf

def send_alert(interval, price):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f"📊 *BTCUSDT {interval} UPDATE*

💰 Price: *{price:.2f}* USD
🕒 Time: {timestamp}"
    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

def monitor(interval, sleep_sec):
    prices = []
    while True:
        try:
            price = fetch_price(PAIR)
            prices.append(price)
            if len(prices) > 12:
                prices.pop(0)
            chart = generate_chart(prices, interval)
            send_alert(interval, price)
            bot.send_photo(chat_id=CHAT_ID, photo=chart)
            time.sleep(sleep_sec)
        except Exception as e:
            bot.send_message(chat_id=CHAT_ID, text=f"⚠️ Error ({interval}): {str(e)}")
            time.sleep(10)

threading.Thread(target=monitor, args=("5M", 300)).start()
threading.Thread(target=monitor, args=("15M", 900)).start()
threading.Thread(target=monitor, args=("4H", 14400)).start()
