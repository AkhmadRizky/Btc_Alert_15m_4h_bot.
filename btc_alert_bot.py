import os
import asyncio
from telegram import Bot, ParseMode
from telegram.constants import ParseMode
from telegram.error import TelegramError
from binance.client import Client
from io import BytesIO
import matplotlib.pyplot as plt
from datetime import datetime

# === CONFIGURATIONS ===
BOT_TOKEN = "7587053152:AAHbdoQc-iMHdq66_8Zwm7IFAbkFHU-8ouU"
CHAT = "5154881695"
PAIR = "BTCUSDT"
LEVEL_LOW = 102500
LEVEL_HIGH = 104200

# === INITIALIZE ===
TG_BOT = Bot(token=BOT_TOKEN)
BINANCE = Client()

# === GENERATE PRICE CHART (SINGLE LINE PLOT) ===
def generate_chart_image(pair, price):
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [price - 100, price, price + 100], marker='o')
    ax.set_title(f"{pair} Price Alert")
    ax.set_ylabel("Price")
    ax.set_xlabel("Time")
    ax.grid(True)

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)
    return buffer

# === MONITOR & SEND ALERT ===
async def check_price():
    while True:
        try:
            ticker = BINANCE.get_symbol_ticker(symbol=PAIR)
            price = float(ticker['price'])
            print(f"📊 BTCUSDT price: {price}")

            if price <= LEVEL_LOW or price >= LEVEL_HIGH:
                sinyal = "🚨 Harga tembus batas!"
                img = generate_chart_image(PAIR, price)

                await TG_BOT.send_message(chat_id=CHAT, text=f"{sinyal} pada {PAIR}", parse_mode=ParseMode.HTML)
                await TG_BOT.send_photo(chat_id=CHAT, photo=img)

        except TelegramError as te:
            print(f"Telegram Error: {te}")
        except Exception as e:
            print(f"Error: {e}")

        await asyncio.sleep(60)  # Cek setiap 1 menit

# === RUN BOT ===
if __name__ == "__main__":
    asyncio.run(check_price())
