import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import asyncio
import os
from asgiref.sync import sync_to_async

from shared.s3 import S3Client, S3_ACCESS_KEY, S3_SECRET_ACCESS_KEY, S3_ENDPOINT, S3_BUCKET_NAME
import io
from users.models import CustomUser

BOT_API_TOKEN = os.getenv("BOT_API_TOKEN", "plug")

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

    photos = await bot.get_user_profile_photos(user_id, limit=1)

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
    image_bucket_link = f"https://{S3_BUCKET_NAME}.{S3_ENDPOINT}/{file_name}"

    @sync_to_async
    def update_or_create_user():
        user_obj, created = CustomUser.objects.get_or_create(
            telegram_id=user_id,
            defaults={
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "language": user.language_code,
                "is_bot": user.is_bot,
                "image_url": image_bucket_link,
            },
        )
        if not created and user_obj.image_url != image_bucket_link:
            user_obj.image_url = image_bucket_link
            user_obj.save(update_fields=["image_url"])
        return user_obj, created

    user_obj, created = await update_or_create_user()

    if created:
        print(f"✅ Пользователь {user_obj.username} создан.")
    else:
        print(f"ℹ️ Пользователь {user_obj.username} уже существует.")


async def main():
    await dp.start_polling(bot)


asyncio.run(main())
