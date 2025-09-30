import os, json
from datetime import datetime, timezone
from django.contrib.auth import login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User

from .models import TelegramAccount
from .telegram_wbapp import verify_webapp_init_data, parse_init_data


class TelegramWebAppLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        init_data = (request.data or {}).get("initData", "")
        if not bot_token or not init_data:
            return Response({"ok": False, "error": "bad request"}, status=status.HTTP_400_BAD_REQUEST)

        if not verify_webapp_init_data(init_data, bot_token):
            return Response({"ok": False, "error": "verification failed"}, status=status.HTTP_400_BAD_REQUEST)

        items = parse_init_data(init_data)
        try:
            user_json = json.loads(items.get("user", "{}"))
            tg_id = int(user_json["id"])
        except Exception:
            return Response({"ok": False, "error": "invalid user data"}, status=status.HTTP_400_BAD_REQUEST)

        # Upsert TelegramAccount + user
        acc = TelegramAccount.objects.filter(telegram_id=tg_id).select_related("user").first()
        if acc is None:
            user = User.objects.create_user(username=f"tg_{tg_id}")
            acc = TelegramAccount.objects.create(
                user=user,
                telegram_id=tg_id,
                username=user_json.get("username") or "",
                first_name=user_json.get("first_name") or "",
                last_name=user_json.get("last_name") or "",
                photo_url=user_json.get("photo_url") or "",
                auth_date=datetime.now(),
            )
        else:
            user = acc.user
            acc.username = user_json.get("username") or acc.username
            acc.first_name = user_json.get("first_name") or acc.first_name
            acc.last_name = user_json.get("last_name") or acc.last_name
            acc.photo_url = user_json.get("photo_url") or acc.photo_url
            acc.auth_date = datetime.now()
            acc.save()

        # Create a Django session (cookie-based)
        login(request, user)

        return Response({
            "ok": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "telegram_id": acc.telegram_id,
                "telegram_username": acc.username,
                "first_name": acc.first_name,
                "last_name": acc.last_name,
                "photo_url": acc.photo_url,
            }
        }, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        acc = getattr(request.user, "telegram", None)
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "telegram": {
                "id": acc.telegram_id if acc else None,
                "username": acc.username if acc else None,
            }
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"ok": True}, status=status.HTTP_200_OK)

# TODO: сделать вью которая возвращает всю ликвидность пользователя
