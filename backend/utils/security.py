from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError
from jose.exceptions import JWTClaimsError
from config import *

pwd_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")  # 환경 변수에서 로드

def hash_password(password: str) -> str:
    """비밀번호 해싱"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """입력된 비밀번호가 저장된 해시와 일치하는지 확인"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str = Depends(oauth2_scheme)):
    """JWT 토큰 검증"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError: # 이 exception들 어떻게 처리할지 고민 좀 해봐야 할 듯 --------------------------
        return None
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTClaimsError:
        raise HTTPException(status_code=401, detail="Invalid token claims")