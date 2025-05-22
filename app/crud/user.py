# app/crud/user.py
from typing import Optional, List
from datetime import datetime, timezone # Mantenha datetime e timezone
from sqlalchemy.orm import Session # <<< MUDANÇA: Use Session do SQLAlchemy ORM
from sqlalchemy import select, desc # <<< MUDANÇA: Use select, desc do SQLAlchemy principal

from app.models.user import User # Importe o modelo User
from app.schemas.user import UserCreate, UserUpdate, UserPasswordUpdate # Importe os schemas
from app.core.security import get_password_hash # Importe a função de hash de senha

def create_user(user_create: UserCreate, db: Session) -> User:
    """
    Cria um novo usuário no banco de dados.
    Recebe um UserCreate schema e retorna o objeto User salvo no BD.
    """
    hashed_password = get_password_hash(user_create.password)

    # <<< MUDANÇA: Crie a instância do modelo diretamente
    user = User(
        username=user_create.username,
        hashed_password=hashed_password,
        role=user_create.role, # Role já é UserRole do Enum
        points=0, # Default já está no modelo, mas pode ser explícito aqui
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    db.add(user)
    db.commit()
    db.refresh(user) # Refresha o objeto para ter o ID gerado pelo DB
    return user

def get_user_by_id(user_id: int, db: Session) -> Optional[User]:
    """
    Busca um usuário no banco de dados pelo seu ID.
    """
    # <<< MUDANÇA: Use db.get() para buscar por PK (SQLAlchemy 2.0)
    user = db.get(User, user_id)
    return user

def get_user_by_username(username: str, db: Session) -> Optional[User]:
    """
    Busca um usuário no banco de dados pelo seu username.
    """
    # <<< MUDANÇA: Use session.execute(select(...)).scalars().first()
    statement = select(User).where(User.username == username)
    user = db.execute(statement).scalars().first()
    return user

# ----------------------------------------------------
# NOVAS FUNÇÕES CRUD PARA ATUALIZAÇÃO
# ----------------------------------------------------

def update_user_profile(user_id: int, user_update: UserUpdate, db: Session) -> Optional[User]:
    """
    Atualiza os dados de perfil de um usuário (ex: username).
    """
    user = db.get(User, user_id) # Use db.get para buscar
    if not user:
        return None

    # <<< MUDANÇA: Use model_dump() para Pydantic v2
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value) # Atualiza o atributo do objeto User

    user.updated_at = datetime.now(timezone.utc) # Atualiza a data de última alteração
    db.add(user) # Adiciona o objeto atualizado de volta à sessão
    db.commit() # Salva as mudanças no banco de dados
    db.refresh(user) # Atualiza o objeto 'user' com os dados do BD
    return user

def update_user_password(user: User, new_password: str, db: Session) -> User:
    """
    Atualiza a senha de um usuário.
    """
    user.hashed_password = get_password_hash(new_password) # Gera hash da nova senha
    user.updated_at = datetime.now(timezone.utc) # Atualiza a data de última alteração
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_users_ranking(db: Session, limit: Optional[int] = None) -> List[User]:
    """
    Busca todos os usuários, ordenados por pontos em ordem decrescente.
    """
    # <<< MUDANÇA: Use session.execute(select(...)).scalars().all()
    statement = select(User).order_by(desc(User.points)) # Ordena por pontos em ordem decrescente
    if limit:
        statement = statement.limit(limit) # Limita o número de resultados, se especificado
    users = db.execute(statement).scalars().all()
    return users