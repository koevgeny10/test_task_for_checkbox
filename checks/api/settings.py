from datetime import timedelta
from pathlib import Path

from pydantic_settings import BaseSettings


class _Settings(BaseSettings):
    JWT_SIGNING_ALGORITHM: str
    JWT_LIFETIME_MINUTES: int


_settings = _Settings()

JWT_LIFETIME = timedelta(minutes=_settings.JWT_LIFETIME_MINUTES)
JWT_SIGNING_ALGORITHM = _settings.JWT_SIGNING_ALGORITHM

with Path("/opt/app/jwt/jwtRS256.key").open(
    encoding="utf-8",
) as _jwt_private_key_file:
    JWT_PRIVATE_KEY = _jwt_private_key_file.read()

with Path("/opt/app/jwt/jwtRS256.key.pub").open(
    encoding="utf-8",
) as _jwt_public_key_file:
    JWT_PUBLIC_KEY = _jwt_public_key_file.read()
