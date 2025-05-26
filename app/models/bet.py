# app/models/bet.py
from __future__ import annotations # DEVE SER A PRIMEIRA LINHA REAL DE CÓDIGO
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped

from app.core.database import Base # Importar a Base declarativa

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.game import Game

class Bet(Base):
    __tablename__ = "bet"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("user.id"), index=True, nullable=False)
    game_id: Mapped[int] = Column(Integer, ForeignKey("game.id"), index=True, nullable=False)

    home_score_bet: Mapped[int] = Column(Integer, nullable=False)
    away_score_bet: Mapped[int] = Column(Integer, nullable=False)

    is_correct: Mapped[Optional[bool]] = Column(Boolean, nullable=True) # Explicitamente nullable
    points_awarded: Mapped[int] = Column(Integer, default=0, nullable=False) # Default 0 e não nulo

    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relacionamentos
    user: Mapped["User"] = relationship("User", back_populates="bets")
    game: Mapped["Game"] = relationship("Game", back_populates="bets")

    def __repr__(self):
        return f"<Bet(id={self.id}, user_id={self.user_id}, game_id={self.game_id})>"
