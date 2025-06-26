from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth_service import AuthService, LoginRequest, Token

router = APIRouter()
auth_service = AuthService()
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    username = auth_service.verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username

@router.post("/login", response_model=Token)
async def login(login_request: LoginRequest):
    return auth_service.login(login_request.username, login_request.password)

@router.get("/verify")
async def verify_token(current_user: str = Depends(get_current_user)):
    return {"user": current_user, "authenticated": True}

@router.get("/test")
async def test_auth_route():
    return {"message": "Auth router is working!", "status": "ok"}