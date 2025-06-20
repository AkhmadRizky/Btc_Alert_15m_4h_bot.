import os
import asyncio
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from binance.client import Client

# ENV
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT = os.getenv("CHAT_ID")
PAIR = os.getenv("PAIR", "BTCUSDT")
LEVEL_LOW = float(os.getenv("ALERT_LEVEL_LOW", "102500"))
LEVEL_HIGH = float(os.getenv("ALERT_LEVEL_HIGH", "104200"))

TG_BOT = Bot(token=BOT_TOKEN)
BINANCE = Client()

# 🔔 Buat gambar alert level
def generate_chart_image(pair, price):
    img = Image.new('RGB', (600, 200), color=(30, 30, 30))
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    d.text((10, 10), f"ALERT PAIR: {pair}", font=font, fill=(255, 255, 0))
    d.text((10, 50), f"CURRENT PRICE: {price}", font=font, fill=(0, 255, 0))
    d.text((10, 100), f"LEVEL RANGE: {LEVEL_LOW} - {LEVEL_HIGH}", font=font, fill=(255, 255, 255))

    output = BytesIO()
    img.save(output, format='PNG')
    output.seek(0)
    return output

# 🔁 Main loop
async def check_price():
    while True:
        try:
            ticker = BINANCE.get_symbol_ticker(symbol=PAIR)
            price = float(ticker['price'])
            print(f"📊 {PAIR} price: {price}")

            if price <= LEVEL_LOW or price >= LEVEL_HIGH:
                msg = f"🚨 Sinyal BTC Alert 🚨\n\nPAIR: <b>{PAIR}</b>\nPRICE: <code>{price}</code>"
                img = generate_chart_image(PAIR, price)

                await TG_BOT.send_message(chat_id=CHAT, text=msg, parse_mode=ParseMode.HTML)
                await TG_BOT.send_photo(chat_id=CHAT, photo=img)

        except TelegramError as e:
            print(f"❌ Telegram Error: {e}")
        except Exception as ex:
            print(f"⚠️ Other Error: {ex}")

        await asyncio.sleep(60)  # delay 1 menit

# ▶️ Start bot
if __name__ == "__main__":
    asyncio.run(check_price())
