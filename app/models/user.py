# # app/models/user.py
# from __future__ import annotations
# from typing import Optional, List, TYPE_CHECKING
# from app.core.database import Base # Importar a Base declarativa
# # REMOVA ESTA LINHA: from sqlmodel import Field # Remova Field se não estiver usando-o para Column
# from sqlalchemy.orm import Mapped, relationship
# from datetime import datetime, timezone
# import enum
# from enum import Enum
# from sqlalchemy import Enum as SQLAlchemyEnum
# from sqlalchemy import Column, Integer, String, DateTime, Boolean

# if TYPE_CHECKING:
#     from app.models.bet import Bet


# class UserRole(str, Enum):
#     USER = "user"
#     ADMIN = "admin"

# class User(Base): # Herda de Base
#     __tablename__ = "user"

#     id: Mapped[int] = Column(Integer, primary_key=True, index=True)
#     username: Mapped[str] = Column(String(50), unique=True, index=True, nullable=False)
#     hashed_password: Mapped[str] = Column(String(255), nullable=False)
#     role: Mapped[UserRole] = Column(
#         SQLAlchemyEnum(UserRole, name="user_roles"), default=UserRole.USER, nullable=False
#     )
#     points: Mapped[int] = Column(Integer, default=0, nullable=False)
#     is_active: Mapped[bool] = Column(Boolean, default=True, nullable=False)
#     created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
#     updated_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

#     bets: Mapped[List["Bet"]] = relationship("Bet", back_populates="user")

# app/models/user.py
from __future__ import annotations # DEVE SER A PRIMEIRA LINHA REAL DE CÓDIGO
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
import enum

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship, Mapped

from app.core.database import Base # Importar a Base declarativa

if TYPE_CHECKING:
    from app.models.bet import Bet # Para type hinting

class UserRole(str, enum.Enum): # Usar enum.Enum padrão do Python
    USER = "user"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    username: Mapped[str] = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = Column(String(255), nullable=False) # Aumentar se usar bcrypt forte
    role: Mapped[UserRole] = Column(SQLAlchemyEnum(UserRole, name="user_role_enum"), default=UserRole.USER, nullable=False)
    points: Mapped[int] = Column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = Column(Boolean, default=True, nullable=False) # Adicionado is_active
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relacionamento com Bet
    # A string "Bet" será resolvida pelo SQLAlchemy
    bets: Mapped[List["Bet"]] = relationship("Bet", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
