"""
Authentication utilities for driaClaude
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from loguru import logger

from app.config import settings

security = HTTPBearer(auto_error=False)

class AuthHandler:
    """Handle authentication for API endpoints"""
    
    def __init__(self):
        self.secret = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60 * 24  # 24 hours
    
    def encode_token(self, user_id: str) -> str:
        """Generate JWT token"""
        payload = {
            'exp': datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)
    
    def decode_token(self, token: str) -> str:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token has expired'
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token'
            )
    
    def verify_api_key(self, api_key: str) -> bool:
        """Verify API key"""
        return api_key == settings.API_KEY

auth_handler = AuthHandler()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[str]:
    """Get current authenticated user"""
    if not settings.ENABLE_AUTH:
        return "anonymous"
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # Check if it's a Bearer token (JWT)
    if credentials.scheme.lower() == "bearer":
        token = credentials.credentials
        
        # First check if it's an API key
        if auth_handler.verify_api_key(token):
            return "api_user"
        
        # Otherwise try to decode as JWT
        try:
            user_id = auth_handler.decode_token(token)
            return user_id
        except HTTPException:
            raise
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication scheme"
    )

async def optional_auth(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[str]:
    """Optional authentication - returns None if not authenticated"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None