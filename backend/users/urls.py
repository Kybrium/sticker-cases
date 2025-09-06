from django.urls import path
from .views import TelegramWebAppLoginView, MeView, LogoutView

urlpatterns = [
    path("telegram-webapp/", TelegramWebAppLoginView.as_view(), name="tg-webapp-login"),
    path("me/", MeView.as_view(), name="me"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
