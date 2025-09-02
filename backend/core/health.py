from django.http import JsonResponse
from django.db import connection

def healthz(_request):
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT 1;")
        return JsonResponse({"ok": True}, status=200)
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)