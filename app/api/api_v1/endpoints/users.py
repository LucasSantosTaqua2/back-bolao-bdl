# app/api/v1/endpoints/users.py
from typing import Annotated, List, Any

from fastapi import APIRouter, Depends, HTTPException, status, Response # Response importado
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone # timezone importado

from app.core.security import create_access_token, verify_password, Token
from app.core.database import get_session
from app.core.security import get_current_user, get_current_active_admin # Funções de segurança
# CRUD functions
from app.crud.user import (
    create_user,
    get_user_by_username,
    get_user_by_id, # Embora não usado diretamente aqui, é bom ter se necessário
    update_user_profile,
    update_user_password,
    get_users_ranking
)
# Models and Schemas
from app.models.user import User, UserRole # Modelos SQLAlchemy
from app.schemas.user import UserCreate, UserRead, UserUpdate, UserPasswordUpdate # Schemas Pydantic

router = APIRouter()

# --------------------------------------------------
# Endpoint de Registro de Usuário
# --------------------------------------------------
@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user_create: UserCreate, db: Session = Depends(get_session)):
    """
    Registra um novo usuário no sistema.
    Retorna os dados do usuário registrado (sem a senha).
    """
    db_user = get_user_by_username(user_create.username, db)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome de usuário já registrado."
        )
    user = create_user(user_create, db)
    return user

# --------------------------------------------------
# Endpoint de Login (Obtenção de Token JWT)
# --------------------------------------------------
@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_session)
):
    """
    Realiza o login de um usuário e retorna um token de acesso JWT.
    Requer 'username' e 'password' no corpo da requisição (x-www-form-urlencoded).
    """
    user = get_user_by_username(form_data.username, db)
    if not user or not user.is_active: # Adicionada verificação de is_active
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas ou usuário inativo",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value} # Usar .value para o Enum
    )
    return {"access_token": access_token, "token_type": "bearer"}


# --------------------------------------------------
# Endpoint de Perfil (Obter e Atualizar)
# --------------------------------------------------
@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Retorna as informações do usuário atualmente logado.
    Esta rota requer um token JWT válido.
    """
    return current_user

@router.put("/me", response_model=UserRead)
async def update_users_me(
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_session)
):
    """
    Atualiza as informações do usuário atualmente logado (ex: username).
    Esta rota requer um token JWT válido.
    """
    if user_update.username and user_update.username != current_user.username:
        existing_user = get_user_by_username(user_update.username, db)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Novo nome de usuário já está em uso."
            )

    updated_user = update_user_profile(current_user.id, user_update, db)
    # A função update_user_profile já deve retornar o usuário atualizado ou None
    if not updated_user: # Isso pode não ser necessário se update_user_profile sempre retornar o usuário ou levantar erro
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, # Ou 500 se for um erro inesperado
            detail="Usuário não encontrado ou falha ao atualizar."
        )
    return updated_user

# --------------------------------------------------
# Endpoint para Alterar Senha
# --------------------------------------------------
@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_my_password(
    password_update: UserPasswordUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_session)
):
    """
    Permite que o usuário logado altere sua senha.
    Requer a senha atual para verificação.
    """
    if not verify_password(password_update.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha atual incorreta."
        )

    update_user_password(current_user, password_update.new_password, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT) # Response está definido


# --------------------------------------------------
# ENDPOINT: Ranking de Usuários
# --------------------------------------------------
@router.get("/ranking", response_model=List[UserRead])
async def read_users_ranking(
    # Removida a dependência de current_user se o ranking for público
    # Se o ranking for protegido, adicione: current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_session)
):
    """
    Retorna a classificação de todos os usuários, ordenada por pontos.
    """
    ranking_users = get_users_ranking(db)
    return ranking_users

# --------------------------------------------------
# ENDPOINT: ADMINISTRAÇÃO DE USUÁRIOS
# (Exige que o usuário seja um administrador)
# --------------------------------------------------
@router.get("/admin/users", response_model=List[UserRead])
async def read_all_users(
    current_admin: Annotated[User, Depends(get_current_active_admin)], # Protegido para admin
    db: Session = Depends(get_session)
):
    """
    Retorna uma lista de todos os usuários no sistema (apenas para administradores).
    """
    users_stmt = select(User) # Cria o statement
    users = db.execute(users_stmt).scalars().all() # Executa e obtém todos os resultados
    return users
