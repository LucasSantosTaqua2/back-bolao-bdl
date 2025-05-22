# app/crud/bet.py
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session # Use Session do SQLAlchemy ORM
from sqlalchemy import select # Use select do SQLAlchemy principal
from sqlalchemy import exc # Para lidar com exceções de banco de dados (opcional)

from app.models.bet import Bet # Importe o modelo Bet
from app.models.game import Game # Importe o modelo Game (necessário para a query)
from app.schemas.bet import BetCreate # Importe o schema BetCreate

# Se você tiver um CRUD de usuário, pode importar a função de criação aqui, se necessário.
# from app.crud.user import get_user_by_id # Exemplo

def create_bet(bet_create: BetCreate, user_id: int, db: Session) -> Bet:
    """
    Cria uma nova aposta no banco de dados para um usuário específico.
    """
    db_bet = Bet(
        user_id=user_id,
        game_id=bet_create.game_id,
        home_score_bet=bet_create.home_score_bet,
        away_score_bet=bet_create.away_score_bet,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(db_bet)
    db.commit()
    db.refresh(db_bet)
    return db_bet

def get_bet_by_id(bet_id: int, db: Session) -> Optional[Bet]:
    """
    Busca uma aposta pelo seu ID.
    """
    return db.get(Bet, bet_id)

def get_user_bet_for_game(user_id: int, game_id: int, db: Session) -> Optional[Bet]:
    """
    Busca uma aposta específica de um usuário para um determinado jogo.
    """
    statement = select(Bet).where(Bet.user_id == user_id, Bet.game_id == game_id)
    return db.execute(statement).scalars().first()

def get_all_bets(db: Session) -> List[Bet]:
    """
    Retorna todas as apostas no banco de dados (útil para admins).
    """
    return db.execute(select(Bet)).scalars().all()

# --------------------------------------------------
# FUNÇÃO PARA A PÁGINA DE APOSTAS:
# --------------------------------------------------
def get_user_bets_by_round(user_id: int, round_number: int, db: Session) -> List[Bet]:
    """
    Busca todas as apostas feitas por um usuário para uma rodada específica.
    """
    # Usamos .join(Game) para poder filtrar e ordenar pela tabela de Game
    statement = select(Bet).join(Game).where(
        Bet.user_id == user_id,
        Game.round_number == round_number
    ).order_by(Game.game_datetime) # Ordenar pela data/hora do jogo

    return db.execute(statement).scalars().all()

def update_bet_scores(bet_id: int, home_score_bet: int, away_score_bet: int, db: Session) -> Optional[Bet]:
    """
    Atualiza os placares apostados de uma aposta existente.
    """
    bet = db.get(Bet, bet_id)
    if not bet:
        return None
    
    bet.home_score_bet = home_score_bet
    bet.away_score_bet = away_score_bet
    bet.updated_at = datetime.now(timezone.utc)

    db.add(bet)
    db.commit()
    db.refresh(bet)
    return bet