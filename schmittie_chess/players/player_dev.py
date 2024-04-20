from typing import Iterator
from ..config import const
from ..utils import gives_check
from .player import BasePlayer
from .player_minimax import generate_legal_moves
from .evaluation import Evaluator
from argparse import Namespace
import numpy as np
import chess
import logging


class PlayerDev(BasePlayer):
    def __init__(self, seed: int | None = 1337, color: bool = False) -> None:
        super().__init__(seed, color)
        self.logger = logging.getLogger('BaseMiniMaxPlayer')
        self.n_iter = 0
        self.hash_map: dict[str, Namespace] = {} 
        self.move_map: dict = {}
        self.n_iters: dict = {}
        self.move_handler = MoveHandler(color=color)
        self.evaluator = Evaluator(color)

    def __repr__(self) -> str:
        return f'PlayerDev(color={self.color})'

    def choose_move(self, state: chess.Board, time_left: int, depth: int = 4, *, move_fraction: float = 0.2) -> chess.Move | None:
        self.n_iter = 0
        if not self.color:
            state = state.mirror()
            self.logger.debug('Player is black, mirroring board')
        eval, move = self.minimax(state, True, depth,)
        self.n_iters[move] = self.n_iter
        self.logger.info(f'PlayerDev:     Used {self.n_iter:.0f} Iterations')
        self.logger.info(f'Finished evaluating position up to depth: {depth}')
        self.logger.info(f'Best move found: {move} with evaluation: {eval:.2f}')
        if not self.color:
            move = self.move_handler._mirror_move(move)
            self.logger.debug(f'Player is black, mirrored move to: {move}')
        return move
    
    def value_function(self, state: chess.Board) -> float:
        return super().value_function(state)
    
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
        self.n_iter += 1
        if state.is_game_over():
            return _eval(state, player), move
        if not depth: 
            return self._eval_with_captures(state, player, alpha, beta), move
        
        # moves: list[chess.Move] = self.move_handler.generate_legal_moves(state)
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

    def _eval_with_captures(self, state: chess.Board, player: bool, alpha: float, beta: float) -> float:
        """ quiesence search that aims to probe a position until it is 'quiet'. 
        Quiet here means that there are no good captures left in the position, 
        consider for example that the maximum depth of the minimax search is reached 
        in a position where QxP occured, the static evaluation would return a score indicating that
        a pawn has been won, even though in fact, the next move of the computer would be PxQ. 
        In order to limit the number of explored leafs, delta pruning is employed. 
        Takes:
            - state: (Board) the position to evaluate
            - player: (bool) the player to maximise
            - alpha: (float) the alpha parameter of the minimax with pruning
            - beta: (float) the beta parameter of the minimax with pruning
        Returns:
            - (float) the quiet evaluation score of the position
        """
        score: float = self.evaluator(state, self.color)
        if score >= beta:
            return beta
        alpha = max(alpha, score)

        moves: Iterator[chess.Move] = state.generate_legal_captures()
        for move in moves:
            state.push(move)
            score = -1 * self._eval_with_captures(state, not player, -beta, -alpha)
            state.pop()

            if score >= beta:
                return beta
            alpha = max(alpha, score)

        return alpha


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

        return value 


class MoveHandler:
    def __init__(self, color: bool) -> None:
        self.move_stack: dict[chess.Move, float] = {}
        self.color = color
        return None
    
    @staticmethod
    def _mirror_move(move: chess.Move | None) -> chess.Move | None:
        if move is None:
            return None
        move_str: str = str(move)
        new_move: str = (move_str[0] + const.ROW_INV[move_str[1]] 
                         + move_str[2] + const.ROW_INV[move_str[3]])
        new_move += move_str[4:]
        return chess.Move.from_uci(new_move)

    def generate_legal_moves(self, state: chess.Board) -> list[chess.Move]:
        legal_moves: dict[chess.Move, float] = {}
        for move in state.legal_moves:
            score: float = 0
            legal_moves[move] = score
            target_square: chess.Square = move.to_square
            source_square: chess.Square = move.from_square
            source_piece: chess.Piece | None = state.piece_at(source_square)
            target_piece: chess.Piece | None = state.piece_at(target_square)

            # currently removed because its too slow for the benefits
            # # bitmaps for attackers und defenders of given square
            # defender_bitmap: chess.SquareSet = state.attackers(not self.color, target_square)
            # attacker_bitmap: chess.SquareSet = state.attackers(self.color, target_square)
            # enemy_pawns: chess.SquareSet = chess.SquareSet(state.pieces_mask(chess.PAWN, not self.color))
            # defending_pawns = defender_bitmap & enemy_pawns
            
            # prioritise giving check
            if state.gives_check(move):
                score += 100

            # prioritise capturing enemy pieces with lower value pieces
            if target_piece:  
                score += (15 * const.VALUE_HASH[target_piece.piece_type] 
                          - const.VALUE_HASH[source_piece.piece_type])
                # # deprioritise putting a piece on a square that is attacked less times than defended
                # if len(defender_bitmap) > len(attacker_bitmap):
                #     score -= 1 * const.VALUE_HASH[source_piece.piece_type]

            # prioritise moves with promotions
            if promotion_piece := move.promotion:
                score += const.VALUE_HASH[promotion_piece]

            legal_moves[move] = score

        sorted_list = sorted([(key, score) for key, score in legal_moves.items()], key=lambda x: x[1])
        return [it[0] for it in sorted_list[::-1]]
    
    # def generate_legal_moves(self, state: chess.Board) -> list[chess.Move]:
    #     legal_moves: dict[chess.Move, float] = {}
    #     for move in state.legal_moves:
    #         score: float = 0.
    #         target_square: chess.Square = move.to_square
    #         source_square: chess.Square = move.from_square
    #         source_piece: chess.Piece | None = state.piece_at(source_square)
    #         target_piece: chess.Piece | None = state.piece_at(target_square)

    #         defender_bitmap: chess.SquareSet = state.attackers(not self.color, target_square)
    #         attacker_bitmap: chess.SquareSet = state.attackers(self.color, target_square)
    #         enemy_pawns: chess.SquareSet = chess.SquareSet(state.pieces_mask(chess.PAWN, not self.color))
    #         defending_pawns = defender_bitmap & enemy_pawns

    #         # prioritise giving check
    #         if state.gives_check(move):
    #             score += 200

    #         # put priority on capturing most valuable enemy piece with our least valuable piece
    #         if target_piece:  
    #             score += (25 * const.VALUE_HASH[target_piece.piece_type] 
    #                       - const.VALUE_HASH[source_piece.piece_type])
    #             # deprioritise putting a piece on a square that is attacked less times than defended
    #             if len(defender_bitmap) > len(attacker_bitmap):
    #                 score -= 1 * const.VALUE_HASH[source_piece.piece_type]
            
    #         # put priority on moves with promotions
    #         if promotion_piece := move.promotion:
    #             score += const.VALUE_HASH[promotion_piece]

    #         # deprioritise putting a piece on a square that is attacked by enemy pawns
    #         if len(defending_pawns):
    #             score -= const.VALUE_HASH[source_piece.piece_type]

    #         legal_moves[move] = score
    #     sorted_list = sorted([(key, score) for key, score in legal_moves.items()], key=lambda x: x[1])
    #     return [it[0] for it in sorted_list[::-1]]