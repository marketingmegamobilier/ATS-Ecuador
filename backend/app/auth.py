import os
import logging
import secrets
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

logger = logging.getLogger("auth")

ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASS = os.getenv("ADMIN_PASS")

logger.info(f"ADMIN_USER configurado: {'SI' if ADMIN_USER else 'NO'}")
logger.info(f"ADMIN_PASS configurado: {'SI' if ADMIN_PASS else 'NO'}")
if ADMIN_PASS:
    logger.info(f"ADMIN_PASS valor (primeros 3 chars): {ADMIN_PASS[:3]}...")

# Tokens activos en memoria
active_tokens: set = set()

security = HTTPBearer(auto_error=False)

router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    if credentials is None or credentials.credentials not in active_tokens:
        raise HTTPException(status_code=401, detail="No autorizado")
    return credentials.credentials


@router.post("/auth/login", response_model=TokenResponse)
def login(request: LoginRequest):
    logger.info(f"Intento login - usuario: '{request.username}'")
    logger.info(f"ADMIN_USER env: '{ADMIN_USER}'")
    logger.info(f"Password recibido: '{request.password}'")
    logger.info(f"ADMIN_PASS env: '{ADMIN_PASS}'")

    if not ADMIN_USER or not ADMIN_PASS:
        logger.error("Variables ADMIN_USER o ADMIN_PASS no configuradas")
        raise HTTPException(status_code=500, detail="Credenciales no configuradas en el servidor")

    if request.username != ADMIN_USER or request.password != ADMIN_PASS:
        logger.warning(f"Credenciales incorrectas - user match: {request.username == ADMIN_USER}, pass match: {request.password == ADMIN_PASS}")
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    token = secrets.token_urlsafe(32)
    active_tokens.add(token)
    logger.info(f"Login exitoso para usuario: {request.username}")
    return TokenResponse(access_token=token)


@router.post("/auth/logout")
def logout(token: str = Depends(verify_token)):
    active_tokens.discard(token)
    return {"message": "Sesion cerrada"}
