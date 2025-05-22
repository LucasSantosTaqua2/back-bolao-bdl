# # app/models/game.py
# from __future__ import annotations
# from typing import Optional, List, TYPE_CHECKING
# from datetime import datetime, timezone
# from app.core.database import Base # Importar a Base declarativa
# # REMOVA ESTA LINHA: from sqlmodel import Field # Remova Field se não estiver usando-o para Column
# from sqlalchemy.orm import Mapped, relationship
# import enum
# from enum import Enum
# from sqlalchemy import Enum as SQLAlchemyEnum
# from sqlalchemy import Column, Integer, String, DateTime

# if TYPE_CHECKING:
#     from app.models.bet import Bet


# class GameStatus(str, Enum):
#     SCHEDULED = "scheduled"
#     FINISHED = "finished"
#     POSTPONED = "postponed"
#     CANCELED = "canceled"

# class Game(Base): # Herda de Base
#     __tablename__ = "game"

#     id: Mapped[int] = Column(Integer, primary_key=True, index=True)
#     round_number: Mapped[int] = Column(Integer, nullable=False, index=True)
#     home_team: Mapped[str] = Column(String(100), nullable=False)
#     away_team: Mapped[str] = Column(String(100), nullable=False)
#     game_datetime: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)

#     home_score: Mapped[Optional[int]] = Column(Integer)
#     away_score: Mapped[Optional[int]] = Column(Integer)
#     status: Mapped[GameStatus] = Column(SQLAlchemyEnum(GameStatus, name="game_statuses"), default=GameStatus.SCHEDULED, nullable=False)

#     created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
#     updated_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

#     bets: Mapped[List["Bet"]] = relationship("Bet", back_populates="game")

# app/models/game.py
from __future__ import annotations # DEVE SER A PRIMEIRA LINHA REAL DE CÓDIGO
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
import enum

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship, Mapped

from app.core.database import Base # Importar a Base declarativa

if TYPE_CHECKING:
    from app.models.bet import Bet

class GameStatus(str, enum.Enum): # Usar enum.Enum padrão do Python
    SCHEDULED = "scheduled"
    FINISHED = "finished"
    POSTPONED = "postponed"
    CANCELED = "canceled"

class Game(Base):
    __tablename__ = "game"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    round_number: Mapped[int] = Column(Integer, nullable=False, index=True)
    home_team: Mapped[str] = Column(String(100), nullable=False)
    away_team: Mapped[str] = Column(String(100), nullable=False)
    game_datetime: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)

    home_score: Mapped[Optional[int]] = Column(Integer, nullable=True) # Explicitamente nullable
    away_score: Mapped[Optional[int]] = Column(Integer, nullable=True) # Explicitamente nullable
    status: Mapped[GameStatus] = Column(SQLAlchemyEnum(GameStatus, name="game_status_enum"), default=GameStatus.SCHEDULED, nullable=False)

    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relacionamento com Bet
    bets: Mapped[List["Bet"]] = relationship("Bet", back_populates="game")

    def __repr__(self):
        return f"<Game(id={self.id}, home_team='{self.home_team}', away_team='{self.away_team}')>"
