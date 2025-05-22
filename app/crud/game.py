# app/crud/game.py
from typing import List, Optional
from datetime import datetime, timezone # Adicione datetime e timezone
from sqlalchemy.orm import Session # <<< MUDANÇA: Use Session do SQLAlchemy ORM
from sqlalchemy import select, desc, delete # <<< MUDANÇA: Use select, desc, delete do SQLAlchemy principal

from app.models.game import Game, GameStatus # Importe o modelo Game
from app.models.bet import Bet # Importe o modelo Bet
from app.models.user import User # Importe o modelo User
from app.schemas.game import GameCreate, GameUpdateResult # Importe os schemas

def create_game(game_create: GameCreate, db: Session) -> Game:
    """
    Cria um novo jogo no banco de dados.
    """
    # Use model_dump() para Pydantic v2 para converter o schema em dict
    game = Game(**game_create.model_dump())
    db.add(game)
    db.commit()
    db.refresh(game) # Refresha o objeto para ter o ID gerado pelo DB
    return game

def get_game_by_id(game_id: int, db: Session) -> Optional[Game]:
    """
    Busca um jogo pelo seu ID.
    """
    return db.get(Game, game_id)

def get_games_by_round(round_number: int, db: Session) -> List[Game]:
    """
    Busca todos os jogos de uma rodada específica.
    """
    statement = select(Game).where(Game.round_number == round_number).order_by(Game.game_datetime)
    return db.execute(statement).scalars().all()

def update_game_result(game_id: int, game_update: GameUpdateResult, db: Session) -> Optional[Game]:
    """
    Atualiza os resultados e o status de um jogo.
    """
    game = db.get(Game, game_id)
    if not game:
        return None
    
    update_data = game_update.model_dump(exclude_unset=True)
    
    # Pre-check original status to see if it's changing to FINISHED
    original_status = game.status

    for key, value in update_data.items():
        setattr(game, key, value)
    
    game.updated_at = datetime.now(timezone.utc)
    db.add(game)
    db.commit() # Comita as mudanças no jogo
    db.refresh(game) # Refresha o objeto Game

    # <<< MUDANÇA AQUI: Removido 'GameStatus.COMPLETED' da condição
    # A lógica deve ser: se o jogo foi finalizado E o status MUDOU para finalizado
    if (game.status == GameStatus.FINISHED) and \
       (original_status != GameStatus.FINISHED): # Apenas verifica se o status original NÃO era FINISHED
        print(f"Jogo {game.id} finalizado. Calculando e distribuindo pontos...")
        calculate_and_award_points(game, db) # CHAMA A FUNÇÃO AQUI
        print("Pontos distribuídos com sucesso para o jogo.")
    
    return game

def get_all_games(db: Session) -> List[Game]:
    """
    Retorna todos os jogos no banco de dados.
    """
    statement = select(Game).order_by(Game.round_number, Game.game_datetime)
    return db.execute(statement).scalars().all()

def get_all_games_for_user(db: Session) -> List[Game]:
    """
    Retorna todos os jogos visíveis para usuários comuns (agendados, finalizados, adiados).
    Exclui jogos cancelados.
    """
    statement = select(Game).where(Game.status != GameStatus.CANCELED).order_by(Game.round_number, Game.game_datetime)
    return db.execute(statement).scalars().all()

def delete_game_by_id(game_id: int, db: Session) -> bool:
    """
    Deleta um jogo específico pelo seu ID.
    Retorna True se o jogo foi encontrado e deletado, False caso contrário.
    """
    game = db.get(Game, game_id)
    if game:
        db.delete(game)
        db.commit()
        return True
    return False

def delete_games_by_round(round_number: int, db: Session) -> int:
    """
    Deleta todos os jogos de uma rodada específica.
    Retorna o número de jogos deletados.
    """
    statement = delete(Game).where(Game.round_number == round_number)
    
    result = db.execute(statement) # Execute a declaração de delete
    db.commit()

    return result.rowcount # Retorne o número de linhas afetadas


# --------------------------------------------------
# Função para Calcular e Atualizar Pontos das Apostas de um Jogo
# --------------------------------------------------
def calculate_and_award_points(game: Game, db: Session):
    """
    Calcula os pontos para todas as apostas de um jogo finalizado
    e atualiza a tabela de apostas e os pontos dos usuários.
    Regra: 1 ponto por placar exato.
    """
    # <<< MUDANÇA AQUI: Removido 'GameStatus.COMPLETED' da condição
    if game.status != GameStatus.FINISHED:
        # Apenas jogos com status FINISHED devem ter pontos calculados
        return

    bets_for_game = db.execute(
        select(Bet).where(Bet.game_id == game.id)
    ).scalars().all()

    for bet in bets_for_game:
        is_correct = False
        points_awarded = 0

        # Regra de Pontuação: APENAS 1 ponto por Placar Exato
        if (game.home_score is not None and game.away_score is not None and
            bet.home_score_bet == game.home_score and bet.away_score_bet == game.away_score):
            is_correct = True
            points_awarded = 1 # Apenas 1 ponto por placar exato
        
        # Se não for placar exato, is_correct permanece False e points_awarded permanece 0.

        # Atualizar a aposta
        bet.is_correct = is_correct
        bet.points_awarded = points_awarded
        bet.updated_at = datetime.now(timezone.utc)
        db.add(bet)

        # Atualizar os pontos do usuário (se ganhou pontos)
        if points_awarded > 0:
            user = db.get(User, bet.user_id)
            if user:
                user.points += points_awarded
                user.updated_at = datetime.now(timezone.utc)
                db.add(user) # Adiciona o usuário atualizado à sessão

    db.commit() # Comita todas as atualizações de aposta e usuário