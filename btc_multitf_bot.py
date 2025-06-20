
import asyncio
from telegram import Bot
from telegram.error import TelegramError
from binance.client import Client
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime

# === CONFIG ===
BOT_TOKEN = "7966133298:AAHzzZtr_z7qn9OHOovdS4JXUGgFZUPtKEo"
CHAT_ID = "5154881695"
PAIR = "BTCUSDT"

# === INIT ===
TG_BOT = Bot(token=BOT_TOKEN)
BINANCE = Client()

# === CHART MAKER ===
def generate_multitf_chart(tf_data):
    fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    timeframes = ['5m', '15m', '1h']

    for idx, tf in enumerate(timeframes):
        times, prices = tf_data[tf]
        axs[idx].plot(times, prices, marker='o')
        axs[idx].set_title(f"{PAIR} - {tf}")
        axs[idx].grid(True)
        axs[idx].set_ylabel("Price")

    axs[2].set_xlabel("Time")
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)
    return buffer

# === TREND DETECTOR ===
def detect_trend(prices):
    if prices[-1] > prices[0]:
        return "Bullish 🔼"
    elif prices[-1] < prices[0]:
        return "Bearish 🔽"
    else:
        return "Konsolidasi ⏸"

# === FETCH PRICE DATA ===
def fetch_tf_data():
    tf_settings = {
        "5m": Client.KLINE_INTERVAL_5MINUTE,
        "15m": Client.KLINE_INTERVAL_15MINUTE,
        "1h": Client.KLINE_INTERVAL_1HOUR
    }
    tf_data = {}
    trend_info = {}

    for tf, interval in tf_settings.items():
        klines = BINANCE.get_klines(symbol=PAIR, interval=interval, limit=10)
        prices = [float(k[4]) for k in klines]
        times = [datetime.fromtimestamp(k[0] / 1000).strftime('%H:%M') for k in klines]
        tf_data[tf] = (times, prices)
        trend_info[tf] = (prices[-1], detect_trend(prices))

    return tf_data, trend_info

# === MAIN BOT LOOP ===
async def run_multitf_bot():
    while True:
        try:
            tf_data, trend_info = fetch_tf_data()

            msg = f"📊 <b>Update Harga BTC/USDT Multi-Timeframe</b>\n\n"
            for tf, (price, trend) in trend_info.items():
                msg += f"🕒 {tf}: <b>{price:.2f}</b> → {trend}\n"

            msg += "\n📈 Grafik terlampir. Update tiap 15 menit."

            chart_img = generate_multitf_chart(tf_data)

            await TG_BOT.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")
            await TG_BOT.send_photo(chat_id=CHAT_ID, photo=chart_img)

        except TelegramError as te:
            print(f"[TelegramError] {te}")
        except Exception as e:
            print(f"[Error] {e}")

        await asyncio.sleep(900)  # 15 menit

# === RUN ===
if __name__ == "__main__":
    asyncio.run(run_multitf_bot())
