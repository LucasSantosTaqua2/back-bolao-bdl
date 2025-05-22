from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.models.user import UserRole  # <--- Importe o Enum UserRole do seu modelo


# Schema Base: Campos comuns para leitura e criação
class UserBase(BaseModel):
    username: str
    role: Optional[UserRole] = UserRole.USER  # <--- Adicionado o campo role aqui, opcional na entrada


# Schema para Criação de Usuário:
# Recebe a senha em texto puro do frontend.
class UserCreate(UserBase):
    password: str  # A senha em texto puro que o usuário envia


# Schema para Leitura de Usuário:
# O que a API retorna, sem a senha com hash, mas com ID, datas e o papel.
class UserRead(UserBase):
    id: int
    role: UserRole  # <--- O campo role é obrigatório na saída
    points: int  # <--- Adicionado o campo 'points' para leitura
    created_at: datetime
    updated_at: datetime

    # Configuração crucial para que o Pydantic possa ler dados de um ORM (como o SQLModel)
    class Config:
        from_attributes = True


# Schema para atualizar o perfil do usuário (ex: username)
# Permite que o username seja opcional para atualização, se nenhum for fornecido, não será atualizado.
class UserUpdate(BaseModel):
    username: Optional[str] = None


# Schema para mudança de senha
# Contém a senha atual para verificação e a nova senha.
class UserPasswordUpdate(BaseModel):
    current_password: str  # Senha atual para verificação
    new_password: str  # Nova senha