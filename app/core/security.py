import hmac
import hashlib

from app.core.config import settings


def hash_api_key(api_key:str) -> str:

    digest = hmac.new(
        key=settings.API_KEY_HMAC_SECRET.encode("utf-8"),
        msg=api_key.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    return digest