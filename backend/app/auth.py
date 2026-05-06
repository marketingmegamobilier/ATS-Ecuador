import os
import secrets
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASS = os.getenv("ADMIN_PASS")

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
    if not ADMIN_USER or not ADMIN_PASS:
        raise HTTPException(status_code=500, detail="Credenciales no configuradas")
    if request.username != ADMIN_USER or request.password != ADMIN_PASS:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    token = secrets.token_urlsafe(32)
    active_tokens.add(token)
    return TokenResponse(access_token=token)


@router.post("/auth/logout")
def logout(token: str = Depends(verify_token)):
    active_tokens.discard(token)
    return {"message": "Sesion cerrada"}
