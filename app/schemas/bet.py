# app/schemas/bet.py

from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, Field

# Esquema para criar uma aposta (o que o frontend envia para um único jogo)
class BetCreate(BaseModel):
    game_id: int
    home_score_bet: int = Field(ge=0) # Garante que o placar seja não negativo
    away_score_bet: int = Field(ge=0) # Garante que o placar seja não negativo

# Esquema para ler uma aposta (o que o backend pode retornar)
class BetRead(BaseModel):
    id: int
    user_id: int
    game_id: int
    home_score_bet: int
    away_score_bet: int
    is_correct: Optional[bool] = None # Se a aposta foi correta (calculado depois)
    points_awarded: Optional[int] = 0 # Pontos ganhos com essa aposta (calculado depois)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # ou orm_mode = True para Pydantic < v2


# Esquema para a requisição de submissão de múltiplas apostas (o que o frontend envia)
class BetsSubmissionRequest(BaseModel):
    bets: List[BetCreate] # Lista de apostas a serem criadas