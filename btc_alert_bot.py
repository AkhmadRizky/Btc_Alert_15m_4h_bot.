import os
import asyncio
from telegram import Bot
from telegram.error import TelegramError
from binance.client import Client
from io import BytesIO
import matplotlib.pyplot as plt

# === CONFIG ===
BOT_TOKEN = "7587053152:AAHbdo0qc-iMHdq66_8Zwm7IFAbkFHU-8ouU"
CHAT = "5154881695"
PAIR = "BTCUSDT"

# === INIT ===
TG_BOT = Bot(token=BOT_TOKEN)
BINANCE = Client()

# === CHART MAKER ===
def generate_chart_image(pair, price):
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [price - 100, price, price + 100], marker='o')
    ax.set_title(f"{pair} Price Update")
    ax.set_ylabel("Price")
    ax.set_xlabel("Time")

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)
    return buffer

# === MONITOR & ALERT ===
async def check_price():
    while True:
        try:
            ticker = BINANCE.get_symbol_ticker(symbol=PAIR)
            price = float(ticker['price'])
            print(f"📊 {PAIR} price: {price}")

            sinyal = f"📢 Update harga {PAIR}: <b>{price}</b>"
            img = generate_chart_image(PAIR, price)

            await TG_BOT.send_message(chat_id=CHAT, text=sinyal, parse_mode="HTML")
            await TG_BOT.send_photo(chat_id=CHAT, photo=img)

        except TelegramError as te:
            print(f"Telegram Error: {te}")
        except Exception as e:
            print(f"Error: {e}")

        await asyncio.sleep(60)

# === RUN ===
if __name__ == "__main__":
    asyncio.run(check_price())
