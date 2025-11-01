import hashlib
import hmac
import json
import time
import urllib.parse

bot_token = ""
telegram_id = 1380639458
auth_date = int(time.time())

user = {
    "id": telegram_id,
    "is_bot": False,
    "first_name": "Valera",
    "username": "valerchik",
    "language_code": "ru"
}

data = {
    "auth_date": str(auth_date),
    "user": json.dumps(user, separators=(",", ":"))  # без пробелов
}

data_check_string = "\n".join(f"{k}={data[k]}" for k in sorted(data.keys()))

secret_key = hashlib.sha256(bot_token.encode()).digest()
hash_ = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

data["hash"] = hash_

init_data = urllib.parse.urlencode(data)
print("initData:")
print(init_data)
