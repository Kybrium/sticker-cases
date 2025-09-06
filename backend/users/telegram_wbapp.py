import hmac, hashlib, urllib.parse

def parse_init_data(init_data: str) -> dict:
    parsed = urllib.parse.parse_qs(init_data, strict_parsing=True)
    return {k: v[0] for k, v in parsed.items()}

def data_check_string(items: dict) -> str:
    return "\n".join(f"{k}={items[k]}" for k in sorted(items.keys()) if k != "hash")

def verify_webapp_init_data(init_data: str, bot_token: str) -> bool:
    items = parse_init_data(init_data)
    if "hash" not in items:
        return False
    check_str = data_check_string(items)
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    expected = hmac.new(secret_key, check_str.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, items["hash"])