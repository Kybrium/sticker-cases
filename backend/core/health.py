from django.db import connection
from django.http import HttpRequest, JsonResponse


def healthz(_request: HttpRequest) -> JsonResponse:
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT 1;")
        return JsonResponse({"ok": True}, status=200)
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)
