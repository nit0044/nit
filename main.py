import os
import logging
import random
import string
import time

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web

# Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Пример: https://your-bot-name.onrender.com

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в переменных окружения!")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

# Параметры доступа
valid_keys = set()
active_users = {}
ACCESS_DURATION_SECONDS = 24 * 60 * 60
IMAGES_COUNT = 10  # Кол-во файлов material1.jpg ... material10.jpg

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def has_active_access(user_id: int) -> bool:
    return user_id in active_users and (time.time() - active_users[user_id]) < ACCESS_DURATION_SECONDS

@dp.message(Command("random"))
async def send_code(message: Message):
    admin_id = 7722389255  # 🔁 Замени на свой Telegram user ID
    if message.from_user.id != admin_id:
        await message.answer("🚫 У вас нет доступа к этой команде.")
        return
    code = generate_code()
    valid_keys.add(code)
    await message.answer(f"`{code}`")

@dp.message(Command("start"))
async def cmd_start(message: Message):
    if has_active_access(message.from_user.id):
        await message.answer("✅ Жеткиликтүүлүк мурда эле активделген. Жөнөтө берсеңиз болот.")
    else:
        await message.answer("🔑 Активациялоо кодуңузду киргизиңиз:")

async def send_random_material(message: Message):
    num = random.randint(1, IMAGES_COUNT)
    filename = f"material{num}.jpg"
    try:
        photo = FSInputFile(filename)
        await message.answer_photo(photo=photo, caption="🎮 Контент жүктөлдү")
    except FileNotFoundError:
        await message.answer("❌ Материал табылган жок.")

@dp.message(F.text)
async def handle_message(message: Message):
    user_id = message.from_user.id
    text = message.text.strip().upper()

    if has_active_access(user_id):
        await send_random_material(message)
    elif text in valid_keys:
        valid_keys.remove(text)
        active_users[user_id] = time.time()
        await message.answer("✅ Код кабыл алынды. Жеткиликтүүлүк 24 саатка активделди.")
        await send_random_material(message)
    else:
        await message.answer("🚫 Код жараксыз. Жаңы кодду киргизиңиз.")

# Webhook-сервер для Render
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

def create_app():
    logging.basicConfig(level=logging.INFO)
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/")
    app.on_startup.append(on_startup)
    return app

app = create_app()
