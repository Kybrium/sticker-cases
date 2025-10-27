class CSPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Разрешаем WebSocket на localhost
        response["Content-Security-Policy"] = "connect-src 'self' ws://127.0.0.1:8000;"
        return response
