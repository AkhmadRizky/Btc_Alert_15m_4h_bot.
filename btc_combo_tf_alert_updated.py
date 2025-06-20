
import os
import asyncio
from telegram import Bot
from telegram.error import TelegramError
from binance.client import Client
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime

# === CONFIG ===
BOT_TOKEN = '7966133298:AAHzzZtr_z7qn9OHOovdS4JXUGgFZUPtKEo'
CHAT_ID = '5154881695'
PAIR = 'BTCUSDT'

# === INIT ===
TG_BOT = Bot(token=BOT_TOKEN)
BINANCE = Client()

# === CHART MAKER ===
def generate_chart_image(pair, price):
    fig, ax = plt.subplots()
    now = datetime.now().strftime('%H:%M')
    ax.plot([1, 2, 3], [price - 100, price, price + 100], marker='o')
    ax.set_title(f'{pair} Update {now}')
    ax.set_ylabel("Price")
    ax.set_xlabel("Time")

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)
    return buffer

# === TF DETECTOR ===
def get_trend_emoji(prices):
    if prices[-1] > prices[-2]:
        return "🔼 Bullish"
    elif prices[-1] < prices[-2]:
        return "🔻 Bearish"
    else:
        return "⚪ Sideways"

# === MONITOR & ALERT ===
async def combo_tf_alert():
    while True:
        try:
            price_now = float(BINANCE.get_symbol_ticker(symbol=PAIR)['price'])

            klines_5m = BINANCE.get_klines(symbol=PAIR, interval='5m', limit=3)
            klines_15m = BINANCE.get_klines(symbol=PAIR, interval='15m', limit=3)
            klines_4h = BINANCE.get_klines(symbol=PAIR, interval='4h', limit=3)

            close_5m = [float(k[4]) for k in klines_5m]
            close_15m = [float(k[4]) for k in klines_15m]
            close_4h = [float(k[4]) for k in klines_4h]

            trend_5m = get_trend_emoji(close_5m)
            trend_15m = get_trend_emoji(close_15m)
            trend_4h = get_trend_emoji(close_4h)

            now = datetime.now().strftime('%H:%M')
            msg = (
                f"📊 <b>BTC/USDT - MultiTF Update</b>\n"
                f"🕐 Waktu: {now} WIB\n\n"
                f"⏱️ TF 5m  ➤ {trend_5m}\n"
                f"⏱️ TF 15m ➤ {trend_15m}\n"
                f"🕓 TF 4H  ➤ {trend_4h}\n\n"
                f"💵 Harga Sekarang: <b>{price_now}</b>\n\n"
                f"🔎 Sinyal:\n"
                f"- TF 5m cocok untuk scalping jika Bullish\n"
                f"- TF 4H amati potensi reversal atau breakout\n\n"
                f"📉 Chart Lengkap: https://www.tradingview.com/chart/?symbol=BINANCE:{PAIR}\n"
                f"⚠️ Gunakan manajemen risiko!"
            )

            chart_img = generate_chart_image(PAIR, price_now)

            await TG_BOT.send_message(chat_id=CHAT_ID, text=msg, parse_mode='HTML')
            await TG_BOT.send_photo(chat_id=CHAT_ID, photo=chart_img)

        except TelegramError as te:
            print(f"[Telegram Error] {te}")
        except Exception as e:
            print(f"[General Error] {e}")

        await asyncio.sleep(900)

# === RUN ===
if __name__ == "__main__":
    asyncio.run(combo_tf_alert())
