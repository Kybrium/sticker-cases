import base64
from nacl.signing import SigningKey
from typing import Dict


def generate_keypair() -> Dict[str, str]:
    """
    Генерирует пару ключей Ed25519 для тестов.
    :return: dict { "private": str, "public": str }
    """
    signing_key = SigningKey.generate()
    verify_key = signing_key.verify_key

    private_key_b64 = base64.b64encode(bytes(signing_key)).decode()
    public_key_b64 = base64.b64encode(bytes(verify_key)).decode()

    return {"private": private_key_b64, "public": public_key_b64}


def generate_signature_for_message(private_key: str, message: str, public_key: str) -> Dict[str, str]:
    """
    Подписывает сообщение и возвращает структуру для API.
    :param private_key: base64 приватный ключ
    :param message: строка вида key=value&key=value
    :param public_key: base64 публичный ключ
    :return: dict { "signature": ..., "message": ..., "public": ... }
    """
    priv_key_bytes = base64.b64decode(private_key)
    signing_key = SigningKey(priv_key_bytes)
    signed = signing_key.sign(message.encode())
    signature_b64 = base64.b64encode(signed.signature).decode()

    return {
        "signature": signature_b64,
        "message": message,
        "public": public_key
    }


if __name__ == "__main__":
    # генерируем тестовую пару ключей
    keys = generate_keypair()
    priv = keys["private"]
    pub = keys["public"]

    msg = "wallet=v-syrom-formate-kosh&telegram_id=123456789&timestamp=1759310239&nonce=WhrzVe0nYMBHIWC21SMp2BC3eh0WbKJ5"

    signed = generate_signature_for_message(priv, msg, pub)
    print(signed)
