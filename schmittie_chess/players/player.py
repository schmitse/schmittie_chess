from ..config import const
from chess import engine
import time
import chess
import numpy as np


class HumanPlayer:
    def __init__(self, name: str = 'Schmittie', color: bool = True) -> None:
        self.name: str = name
        self.auto = False


class BasePlayer:
    """ basic player class for the game """
    def __init__(self, seed: int | None = 1337, color: bool = False) -> None:
        self.rng: np.random.Generator = np.random.default_rng(seed=seed)
        self.color: bool = color
        self.auto = True
        return None
    
    def choose_move(self, state: chess.Board, time_left: int, *, 
                    move_fraction: float = 0.2) -> chess.Move:
        """ choose a move to be made based on objective """
        t0 = time.time()
        time.sleep(1)
        legal_moves = list(state.legal_moves)
        best_move = self.rng.choice(range(len(legal_moves)))
        t1 = time.time()
        if t1 - t0 > time_left * move_fraction / 1000:
            return legal_moves[best_move]
        return legal_moves[best_move]
    
    def value_function(self, state: chess.Board) -> float:
        """ value function that assigns a weight based on the current board state """
        value: float = 0.

        for i in range(const.COLS * const.ROWS):
            piece: chess.Piece | None = state.piece_at(i)
            if piece is None:
                continue
            val = const.VALUE_HASH[piece.piece_type] 
            value = value + val if piece.color else value - val

        return value if self.color else -1 * value

class TheFish(BasePlayer):
    def __init__(self, seed: int | None = 1337, color: bool = False) -> None:
        super().__init__(seed, color)
        self.fish: engine.SimpleEngine = engine.SimpleEngine.popen_uci(r'C:\Stockfish\stockfish\stockfish-windows-x86-64-avx2.exe')

    def choose_move(self, state: chess.Board, time_left: int, *, move_fraction: float = 0.2) -> chess.Move | None:
        result = self.fish.play(state, engine.Limit(min(time_left * move_fraction / 1000, 5)))
        return result.move
    