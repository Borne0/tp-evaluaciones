from datetime import datetime, timedelta, timezone

import jwt

from ..config import settings


def create_token(sub: str, perfil: str, **extra) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode({"sub": sub, "perfil": perfil, "exp": exp, **extra}, settings.jwt_secret, algorithm="HS256")
