from datetime import datetime, timedelta, timezone
from typing import Optional, List # Adicionado List

from passlib.context import CryptContext
from jose import JWTError, jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session # Use Session do SQLAlchemy ORM
from sqlalchemy import select # Use select do SQLAlchemy principal

from app.core.database import get_session # Importe sua função para obter a sessão do DB
from app.models.user import User, UserRole # Importe User e UserRole (UserRole para get_current_active_admin)

from app.core.config import settings

# Configuração para hashing de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema de segurança OAuth2 para obter o token do cabeçalho
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/users/token") # Ajuste tokenUrl se necessário

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se uma senha em texto puro corresponde a uma senha hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera o hash de uma senha em texto puro."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria um token de acesso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Classe auxiliar para as credenciais do token que será retornado no login
# Token é um esquema Pydantic puro, então BaseModel é usado.
from pydantic import BaseModel
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Classe para os dados que esperamos encontrar DENTRO do token (o payload)
class TokenData(BaseModel):
    username: Optional[str] = None
    # role: Optional[str] = None


# *** ORDEM CRÍTICA DAS FUNÇÕES DE DEPENDÊNCIA ***
# 1. get_current_user: A mais básica, decodifica o token para obter o usuário.
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    """
    Decodifica o token JWT, verifica sua validade e retorna o objeto User correspondente.
    Levanta HTTPException se o token for inválido ou o usuário não for encontrado.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = session.execute(select(User).where(User.username == token_data.username)).scalars().first()
    if user is None:
        raise credentials_exception
    return user

# 2. get_current_active_user: Depende de get_current_user e verifica se o usuário está ativo.
async def get_current_active_user(
    current_user: User = Depends(get_current_user) # Usa get_current_user (definido acima)
) -> User:
    """
    Retorna o usuário logado e verifica se ele está ativo.
    """
    if not current_user.is_active: # Assumindo que seu modelo User tem um campo 'is_active'
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário inativo")
    return current_user

# 3. get_current_active_admin: Depende de get_current_active_user e verifica se é admin.
async def get_current_active_admin(
    current_user: User = Depends(get_current_active_user) # Usa get_current_active_user (definido acima)
) -> User:
    """
    Retorna o usuário logado e ativo, verificando se ele tem a role de 'admin'.
    """
    # UserRole já está importado no topo do arquivo
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não autorizado: Requer privilégios de administrador")
    return current_user