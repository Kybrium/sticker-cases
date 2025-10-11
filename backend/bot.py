from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import asyncio
import os
import aiohttp
from shared.s3 import S3Client, S3_ACCESS_KEY, S3_SECRET_ACCESS_KEY, S3_ENDPOINT, S3_BUCKET_NAME
import io

PLUG = "plug"

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
BOT_API_TOKEN = os.getenv("BOT_API_TOKEN", PLUG)

s3_client = S3Client(
    access_key=S3_ACCESS_KEY,
    secret_key=S3_SECRET_ACCESS_KEY,
    endpoint_url=S3_ENDPOINT,
    bucket_name=S3_BUCKET_NAME,
)

bot = Bot(token=BOT_API_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start_handler(message: Message):
    user = message.from_user

    user_id = user.id
    first_name = user.first_name
    last_name = user.last_name
    username = user.username
    language_code = user.language_code
    is_bot = user.is_bot

    payload = {
        "telegram_id": user_id,
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "language": language_code,
        "is_bot": is_bot,
        "image_url": None
    }

    photos = await bot.get_user_profile_photos(user_id, limit=1)

    async with aiohttp.ClientSession() as session:
        if photos.total_count == 0:
            await session.post("path", json=payload)
            return

        sizes = photos.photos[0]
        biggest = max(sizes, key=lambda s: s.file_size or 0)

        file = await bot.get_file(biggest.file_id)

        file_bytes = io.BytesIO()
        await bot.download_file(file.file_path, destination=file_bytes)
        file_bytes.seek(0)

        file_name = f"users/{user_id}.jpg"
        await s3_client.upload_file(file_bytes, file_name)
        image_bucket_link = f"https://{S3_BUCKET_NAME}.{S3_ENDPOINT}/users/{file_name}"
        payload["image_url"] = image_bucket_link

        await session.post(f"{BASE_URL}/api/users/user/", json=payload)


async def main():
    await dp.start_polling(bot)


asyncio.run(main())
