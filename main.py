
import asyncio
import logging
import random
import string
import os
import time
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

TOKEN = "8472699132:AAHaEgned3wfZ1nXqF8w-fVTsqjrxF-ybwc"  # ЗАМЕНИ при необходимости

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

# Коды (одноразовые)
valid_keys = set()

# user_id: время_активации
active_users = {}

# Срок действия — 24 часа
ACCESS_DURATION_SECONDS = 24 * 60 * 60

# Количество изображений (предположим, 10 файлов от material1.jpg до material10.jpg)
IMAGES_COUNT = 10

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def has_active_access(user_id: int) -> bool:
    if user_id not in active_users:
        return False
    activated_at = active_users[user_id]
    return (time.time() - activated_at) < ACCESS_DURATION_SECONDS

@dp.message(Command("random"))
async def send_code(message: Message):
    admin_id = 7130597379  # ← замени на свой Telegram user ID
    if message.from_user.id != admin_id:
        await message.answer("🚫 У вас нет доступа к этой команде.")
        return

    code = generate_code()
    valid_keys.add(code)
    await message.answer(f"`{code}`")

@dp.message(Command("start"))
async def cmd_start(message: Message):
    if has_active_access(message.from_user.id):
        await message.answer("✅ Жеткиликтүүлүк мурда эле активделген. Болгону каалаган билдирүүнү жөнөтүңүз.")
    else:
        await message.answer("🔑 Активациялоо кодуңузду киргизиңиз:")

async def send_random_material(message: Message):
    num = random.randint(1, IMAGES_COUNT)
    filename = f"material{num}.jpg"
    filepath = filename  # Теперь просто имя файла, без папки
    try:
        photo = FSInputFile(filepath)
        await message.answer_photo(photo=photo, caption="🎮 Ваш контент загружен")
    except FileNotFoundError:
        await message.answer("❌ Материал не найден.")

@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    text = message.text.strip().upper()

    if has_active_access(user_id):
        await send_random_material(message)
        return

    if text in valid_keys:
        valid_keys.remove(text)
        active_users[user_id] = time.time()
        await message.answer("✅Код кабыл алынды. Жеткиликтүүлүк 24 саатка активдештирилди.")
        await send_random_material(message)
    else:
        await message.answer("🚫 Код жараксыз же жеткиликтүүлүк мөөнөтү бүткөн.\nЖаңы кодду киргизиңиз.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
