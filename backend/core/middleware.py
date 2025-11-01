from shared.utils import verify_telegram_init_data
from django.utils.deprecation import MiddlewareMixin
from users.models import CustomUser
import os
from django.http import JsonResponse

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
BOT_API_TOKEN = os.getenv("BOT_API_TOKEN", "plug")


class TelegramAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        init_data = request.headers.get("X-Telegram-Init-Data")
        if not init_data:
            return JsonResponse({"status": "error", "message": "Заголовок 'X-Telegram-Init-Data' обязателен"},
                                status=400)

        user_data = verify_telegram_init_data(init_data)
        if not user_data:
            return JsonResponse({"status": "error", "message": "Не верный заголовок 'X-Telegram-Init-Data'"},
                                status=403)

        if user_data.get("is_bot"):
            return JsonResponse({"status": "error", "message": "Не может быть ботом"},
                                status=403)

        telegram_id = user_data["id"]
        username = user_data.get("username", f"tg_{telegram_id}")

        user, _ = CustomUser.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                "username": username,
                "first_name": user_data.get("first_name", ""),
                "last_name": user_data.get("last_name", ""),
                "language_code": user_data.get("language_code", ""),
                "is_bot": user_data.get("is_bot", ""),
            },
        )
        request.user = user
