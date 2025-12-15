import asyncio
from datetime import date

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

file_with_tocken = "tocken_file.txt"
file_with_users = "users.txt"

with open(file_with_tocken, "r") as f:
    T = f.read()

bot = Bot(token=T)
dp = Dispatcher()

user_data = {}

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚬 Перекур")],
        [KeyboardButton(text="📊 Статистика")]
    ],
    resize_keyboard=True
)


def get_user(user_id: int):
    today = str(date.today())

    if user_id not in user_data:
        user_data[user_id] = {
            "today": 0,
            "total": 0,
            "date": today,
            "limit": None
        }

    if user_data[user_id]["date"] != today:
        user_data[user_id]["today"] = 0
        user_data[user_id]["date"] = today

    return user_data[user_id]


@dp.message(Command("start"))
async def start_handler(message: Message):
    get_user(message.from_user.id)

    with open(file_with_users, "a") as f:
        f.write(f"@{message.from_user.username}\n")

    await message.answer(
        f"Привет, {message.from_user.first_name}!"
        "Я считаю сигареты.\n"
        "Команды:\n"
        "/limit <число> — задать дневной лимит\n",
        reply_markup=keyboard
    )


@dp.message(Command("limit"))
async def limit_handler(message: Message):
    user = get_user(message.from_user.id)

    try:
        limit = int(message.text.split()[1])
        if limit <= 0:
            raise ValueError
    except (IndexError, ValueError):
        await message.answer("Используй: /limit 3")
        return

    user["limit"] = limit
    await message.answer(f"Дневной лимит установлен: {limit} 🚭")


@dp.message(lambda m: m.text == "🚬 Перекур")
async def smoke_handler(message: Message):
    user = get_user(message.from_user.id)

    user["today"] += 1
    user["total"] += 1

    text = (
        f"🚬 Учтено\n"
        f"Сегодня: {user['today']}\n"
        f"Всего: {user['total']}"
    )

    if user["limit"] is not None and user["today"] > user["limit"]:
        text += (
            "\n\n⚠️ Лимит превышен.\n"
            "Каждая сигарета усиливает вред для сердца и лёгких."
        )

    await message.answer(text)


@dp.message(lambda m: m.text == "📊 Статистика")
async def stats_handler(message: Message):
    user = get_user(message.from_user.id)

    await message.answer(
        f"📊 Статистика:\n"
        f"Сегодня: {user['today']}\n"
        f"Всего: {user['total']}\n"
        f"Лимит: {user['limit'] if user['limit'] else 'не задан'}"
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
