from ..config import const
from .player import BasePlayer
from argparse import Namespace
import numpy as np
import chess
import logging


def _mirror_move(move: chess.Move | None) -> chess.Move | None:
    if move is None:
        return None
    move_str: str = str(move)
    new_move: str = (move_str[0] + const.ROW_INV[move_str[1]] 
                    + move_str[2] + const.ROW_INV[move_str[3]])
    new_move += move_str[4:]
    return chess.Move.from_uci(new_move)


class PlayerMiniMax(BasePlayer):
    def __init__(self, seed: int | None = 1337, color: bool = False) -> None:
        super().__init__(seed, color)
        self.logger = logging.getLogger('BaseMiniMaxPlayer')
        self.n_iter = 0
        self.hash_map: dict[str, Namespace] = {} 
        self.move_map: dict = {}

    def choose_move(self, state: chess.Board, time_left: int, depth: int = 4, *, move_fraction: float = 0.2) -> chess.Move | None:
        if not self.color:
            state = state.mirror()
            self.logger.warning('Player is black, mirroring board')
        eval, move = self.minimax(state, True, depth,)
        self.logger.info(f'Finished evaluating position up to depth: {depth}')
        self.logger.info(f'Best move found: {move} with evaluation: {eval:.2f}')
        if not self.color:
            move = _mirror_move(move)
            self.logger.warning(f'Player is black, mirrored move to: {move}')
        return move
    
    def value_function(self, state: chess.Board) -> float:
        return super().value_function(state)
    
    def minimax_slow(self, state: chess.Board, player: bool, depth: int, move: chess.Move | None):
        """ minimax without pruning, brute forcing the way through the result tree 
        roughly a factor 100 slower than the minimax with pruning. """
        if not depth or state.is_game_over():
            return _eval(state, player), move
        
        moves: list[chess.Move] = generate_legal_moves(state)
        if player:
            max_score: float = -np.inf
            best_move: None | chess.Move = None
            for move in moves:
                child_board = state.copy()
                child_board.push(move)
                score = self.minimax_slow(child_board, False, depth - 1, best_move)[0]
                max_score = max(score, max_score)
                best_move = move if score == max_score else best_move
            return max_score, best_move
        else:
            min_score: float = np.inf
            best_move: None | chess.Move = None
            for move in moves:
                child_board = state.copy()
                child_board.push(move)
                score = self.minimax_slow(child_board, True, depth - 1, best_move)[0]
                min_score = min(score, min_score)
                best_move = move if score == min_score else best_move
            return min_score, best_move
    
    def minimax(self, state: chess.Board, player: bool, depth: int, alpha: float = -np.inf, 
                beta: float = np.inf, move: chess.Move | None = None) -> tuple[float, chess.Move | None]:
        """ minimax with alpha beta pruning 
        recursively explore the children up to a given maximum depth, pruning the tree based on 
        whether or not the other possible paths already give results that are better / worse
        depending on the player that is maximising their outcome. 
        Takes:
            - state: (chess.Board) the board from which to start
            - player: (bool) the player which is optimising their turn
            - depth: (int) the current depth target
            - alpha: (float) the running alpha pruning parameter, used for player TRUE
            - beta: (float) the running beta pruning parameter, used for player FALSE
            - move: (chess.Move) the best move propagated through the chain. 
        """
        if not depth or state.is_game_over():
            return _eval(state, player), move
        
        moves: list[chess.Move] = generate_legal_moves(state)
        if player:
            best_move: None | chess.Move = None
            for move in moves:
                child_board = state.copy()
                child_board.push(move)
                score = self.minimax(child_board, False, depth - 1, alpha, beta, best_move)[0]
                if score > alpha:
                    alpha = score
                    best_move = move
                if score >= beta:
                    break
            return alpha, best_move
        else:
            best_move: None | chess.Move = None
            for move in moves:
                child_board = state.copy()
                child_board.push(move)
                score = self.minimax(child_board, True, depth - 1, alpha, beta, best_move)[0]
                if score < beta:
                    beta = score
                    best_move = move
                if score <= alpha:
                    break
            return beta, best_move


def generate_legal_moves(state: chess.Board) -> list[chess.Move]:
    legal_moves_captures: dict[chess.Move, None] = dict.fromkeys(mv for mv in state.generate_legal_captures())
    legal_moves_checks: dict[chess.Move, None] = dict.fromkeys(mv for mv in state.legal_moves if state.gives_check(mv))
    legal_moves_all: dict[chess.Move, None] = dict.fromkeys(mv for mv in state.legal_moves)
    legal_moves_ordered: dict[chess.Move, None] = legal_moves_checks | legal_moves_captures | legal_moves_all
    return list(legal_moves_ordered)


def _eval(state: chess.Board, color: bool) -> float:
        if state.is_game_over():
            if state.outcome():
                return np.inf
            return 0
        value: float = 0.

        for i in range(const.COLS * const.ROWS):
            piece: chess.Piece | None = state.piece_at(i)
            if piece is None:
                continue
            val = const.VALUE_HASH[piece.piece_type] 
            value = value + val if piece.color == color else value - val

        return value # if color else -1 * value