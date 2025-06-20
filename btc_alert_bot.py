import os
import asyncio
import requests
from telegram import Bot
from telegram.error import TelegramError
from binance.client import Client
from io import BytesIO
import matplotlib.pyplot as plt

# === CONFIG ===
BOT_TOKEN = "7578053152:AAHbdoQc-iMHdq6_8Zwm7lFAbkFHU-8ouU"
CHAT = "5154881695"
PAIR = "BTCUSDT"
LEVEL_LOW = 102500
LEVEL_HIGH = 104200

# === INIT ===
TG_BOT = Bot(token=BOT_TOKEN)
BINANCE = Client()

# === CHART MAKER ===
def generate_chart_image(pair, price):
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [price - 100, price, price + 100], marker='o')
    ax.set_title(f"{pair} Price Alert")
    ax.set_ylabel("Price")
    ax.set_xlabel("Time")

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)
    return buffer

# === MONITOR & ALERT ===
async def check_price():
    # Tes koneksi awal
    try:
        requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            params={"chat_id": CHAT, "text": "🤖 Bot sudah aktif, siap kirim alert Bos!"}
        )
    except Exception as e:
        print("Gagal kirim pesan awal:", e)

    while True:
        try:
            ticker = BINANCE.get_symbol_ticker(symbol=PAIR)
            price = float(ticker['price'])
            print(f"📉 {PAIR} price: {price}")

            if price <= LEVEL_LOW or price >= LEVEL_HIGH:
                sinyal = "🚨 Harga tembus batas!"
                img = generate_chart_image(PAIR, price)

                # Kirim teks manual via API
                requests.get(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    params={"chat_id": CHAT, "text": f"{sinyal} pada {PAIR}"}
                )

                await TG_BOT.send_photo(chat_id=CHAT, photo=img)

        except TelegramError as te:
            print(f"Telegram Error: {te}")
        except Exception as e:
            print(f"Error: {e}")

        await asyncio.sleep(60)

# === RUN ===
if __name__ == "__main__":
    asyncio.run(check_price())
