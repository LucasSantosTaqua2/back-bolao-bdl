# app/schemas/game.py
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.game import GameStatus

# Schema Base: Campos comuns para criação e leitura (sem ID)
class GameBase(BaseModel):
    round_number: int = Field(..., ge=1, le=38)
    home_team: str
    away_team: str
    game_datetime: datetime

# Schema para Criação de Jogo:
class GameCreate(GameBase):
    pass

# Schema para Atualização de Resultado de Jogo:
class GameUpdateResult(BaseModel):
    # home_score e away_score devem ser opcionais no JSON de entrada,
    # mas se presentes, devem ser int.
    home_score: Optional[int] = Field(default=None, ge=0)
    away_score: Optional[int] = Field(default=None, ge=0)
    status: Optional[GameStatus] = GameStatus.FINISHED

# Schema para Leitura de Jogo:
class GameRead(GameBase):
    id: int
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: GameStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True