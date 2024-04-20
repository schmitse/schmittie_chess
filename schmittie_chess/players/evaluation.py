from ..config import const
import numpy as np
import chess


# early game incentivise pushing central pawns
# and keep pawns on the flank around the king
PAWNS_EARLY_GAME: np.ndarray = np.array([
 0,  0,  0,  0,  0,  0,  0,  0,  # RANK 1
  5, 5,  5,-20,-20, 10, 10, -5,  # RANK 2
 -5,-5,-10,  0,  0,-10, -5,  5,  # RANK 3
 0,  0,  0, 20, 20,  0,  0,  0,  # RANK 4
 5,  5, 10, 25, 25, 10,  5,  5,  # RANK 5
10, 10, 20, 30, 30, 30, 25, 15,  # RANK 6
75, 80, 75, 60, 60, 90, 50, 50,  # RANK 7
 0,  0,  0,  0,  0,  0,  0,  0])  # RANK 8
#A   B   C   D   E   F   G   H

# end game incentivise agressively 
# pushing to try and promote pawns
PAWNS_END_GAME: np.ndarray = np.array([
  0,  0,  0,  0,  0,  0,  0,  0,  # RANK 1
 15, 10, 10,  0,  0,  0,  0,-10,  # RANK 2
  5,  5, -5,  0,  0, -5, -5, -7,  # RANK 3
 15, 10,  0,-10,-10,-10,  0,  0,  # RANK 4
 30, 25, 15,  5,  5,  5, 20, 20,  # RANK 5
100,100,100, 80, 60, 50, 80, 90,  # RANK 6
150,150,125,120,130,120,160,190,  # RANK 7
  0,  0,  0,  0,  0,  0,  0,  0])  # RANK 8
# A   B   C   D   E   F   G   H

# knights should be centralised and 
# not be placed on the rim of the board
KNIGHTS_EARLY_GAME: np.ndarray = np.array([
-50,-40,-30,-30,-30,-30,-40,-50,
-40,-20,  0,  5,  5,  0,-20,-40,
-30,  5, 10, 15, 15, 10,  5,-30,
-30,  0, 15, 20, 20, 15,  0,-30,
-30,  5, 15, 20, 20, 15,  5,-30,
-30,  0, 10, 15, 15, 10,  0,-30,
-40,-20,  0,  0,  0,  0,-20,-40,
-50,-40,-30,-30,-30,-30,-40,-50])
# A   B   C   D   E   F   G   H

# knights still centralised, 
# currently same as early game PST
KNIGHTS_END_GAME: np.ndarray = np.array([
-50,-40,-30,-30,-30,-30,-40,-50,
-40,-20,  0,  5,  5,  0,-20,-40,
-30,  5, 10, 15, 15, 10,  5,-30,
-30,  0, 15, 20, 20, 15,  0,-30,
-30,  5, 15, 20, 20, 15,  5,-30,
-30,  0, 10, 15, 15, 10,  0,-30,
-40,-20,  0,  0,  0,  0,-20,-40,
-50,-40,-30,-30,-30,-30,-40,-50])
# A   B   C   D   E   F   G   H

# bishops can be centralised or fianchettoed
BISHOPS_EARLY_GAME: np.ndarray = np.array([
-20,-10,-10,-10,-10,-10,-10,-20,
-10, 10,  0,  0,  0,  0, 10,-10,
 -5, 10, 10, 10, 10, 10, 10, -5,
-10,  0, 10, 10, 10, 10,  0,-10,
-10,  5,  5, 10, 10,  5,  5,-10,
-10,  0,  5, 10, 10,  5,  0,-10,
-10,  0,  0,  0,  0,  0,  0,-10,
-20,-10,-10,-10,-10,-10,-10,-20])
# A   B   C   D   E   F   G   H

# in the end game bishops can be 
# placed anywhere to make a good job
# their placement is incentivised 
# additionally by a movement score
BISHOPS_END_GAME: np.ndarray = np.array([
  0,  0,  0,  0,  0,  0,  0,  0,
  0,  5,  5,  5,  5,  5,  5,  0,
  0,  5,  7,  7,  7,  7,  5,  0,
  0,  5,  7, 10, 10,  7,  5,  0,
  0,  5,  7, 10, 10,  7,  5,  0,
  0,  5,  7,  7,  7,  7,  5,  0,
  0,  5,  5,  5,  5,  5,  5,  0,
  0,  0,  0,  0,  0,  0,  0,  0])
# A   B   C   D   E   F   G   H

# incentivise castling and taking the 7th rank
ROOKS_EARLY_GAME: np.ndarray = np.array([
-25,-25,  5, 20, 20,  0,-10,-15,
-70, -5, 10,  0,  0,-10,-15,-40,
-30, -5,  0,  0,-20,-15,-20,-40,
-20,  5, -5,  5,  0,-10,-15,-30,
-20,  0, 35, 20, 20,  5,-10,-20,
 15, 50, 45, 20, 35,  0,-10,  0,
 30, 25, 60, 80, 60,  5, -5, -5,
 30, 25, 10, 60, 50,-10,-20,-15])
# A   B   C   D   E   F   G   H

# incentivise taking 7th rank
# and discourage being next to king
ROOKS_END_GAME: np.ndarray = np.array([
-30,-20, -5, 20, 20,  0,  0,  0,
  0,  0,  0,  0,  0,  0,  0,  0,
  0,  0,  0,  0,  0,  0,  0,  0,
  0,  0,  0,  0,  0,  0,  0,  0,
  5,  5,  5,  5,  5,  5,  5,  5,
 10, 10, 10, 10, 10, 10, 10, 10,
 35, 35, 35, 35, 35, 35, 35, 35,
 15, 15, 15, 15, 15, 15, 15, 15])
# A   B   C   D   E   F   G   H

# incentivise moving queen out of starting 
# position and away from 1st rank
QUEENS_EARLY_GAME: np.ndarray = np.array([
-20,-10,-10, -5, -5,-10,-10,-20,
-10,  0,  0,  0,  0,  0,  0,-10,
-10,  5,  5,  5,  5,  5,  0,-10,
  0,  0,  5,  5,  5, 10,  5, -5,
 -5, 10,  5,  5,  5, 15, 10, -5,
-10, 10,  5,  5,  5, 15, 10, -5,
-10, 10,  0,  0, 10, 10, 10, -5,
-20,-10,-10, -5, -5, -5, -5,-10])
# A   B   C   D   E   F   G   H


# centralise queen on the board
# in the end game situations
QUEENS_END_GAME: np.ndarray = np.array([
-50,-35,-20,-10,-10,-20,-35,-50,
-30,-25,-15,-15,-15,-15,-20,-15,
  5, 10, 15, 10, 10, 15,-10,-15,
 20, 30, 35, 35, 35, 30, 20, 10,
 35, 40, 40, 50, 50, 30, 20, 20,
 10, 20, 35, 50, 45, 10, 10,-10,
  0, 30, 20, 50, 50, 30, 20, -5,
  5, 10, 10, 25, 25, 10, 10,  0])
# A   B   C   D   E   F   G   H

# try and make king castle to safety
# disincentivise pushing the king up the board
KINGS_EARLY_GAME: np.ndarray = np.array([
 20, 50, 10,-25,-10, 12, 50, 20,
  5,  5,-10,-40,-40,-10,  5,  0,
-25,-15,-30,-45,-45,-30,-15,-20,
-50,-30,-30,-40,-40,-30,-30,-20,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30])
# A   B   C   D   E   F   G   H

# incentivise pushing and centralising the 
# king in the end game
KINGS_END_GAME: np.ndarray = np.array([
-45,-30,-30,-30,-30,-30,-35,-45,
-30,-25,  0,  0,  0,  0,-25,-30,
-30, -5, 15, 20, 20, 15, -5,-30,
-30,-10, 30, 40, 40, 30,-10,-30,
-30,-10, 30, 40, 40, 30,-10,-30,
-30,-10, 20, 30, 30, 20,-10,-30,
-30,-20,-10,  0,  0,-10,-20,-30,
-50,-40,-30,-20,-20,-30,-40,-50])
# A   B   C   D   E   F   G   H

ZEROS: np.ndarray = np.array([
  0,  0,  0,  0,  0,  0,  0,  0,  # RANK 1
  0,  0,  0,  0,  0,  0,  0,  0,  # RANK 2
  0,  0,  0,  0,  0,  0,  0,  0,  # RANK 3
  0,  0,  0,  0,  0,  0,  0,  0,  # RANK 4
  0,  0,  0,  0,  0,  0,  0,  0,  # RANK 5
  0,  0,  0,  0,  0,  0,  0,  0,  # RANK 6
  0,  0,  0,  0,  0,  0,  0,  0,  # RANK 7
  0,  0,  0,  0,  0,  0,  0,  0]) # RANK 8
# A   B   C   D   E   F   G   H


MAX_PIECES = 32
MIN_PIECES = 2


class Evaluator:
    PAWN: float = const.VALUE_HASH[1]
    KNIGHT: float = const.VALUE_HASH[2]
    BISHOP: float = const.VALUE_HASH[3]
    ROOK: float = const.VALUE_HASH[4]
    QUEEN: float = const.VALUE_HASH[5]
    KING: float = const.VALUE_HASH[6]

    def __init__(self, color: bool) -> None:
        """ evaluation of position with piece square tables """
        self.color = color

        self.pawns_early_game: np.ndarray = PAWNS_EARLY_GAME / 100
        self.pawns_end_game: np.ndarray = PAWNS_END_GAME / 100

        self.knights_early_game: np.ndarray = KNIGHTS_EARLY_GAME / 100
        self.knights_end_game: np.ndarray = KNIGHTS_END_GAME / 100

        self.bishops_early_game: np.ndarray = BISHOPS_EARLY_GAME / 100
        self.bishops_end_game: np.ndarray = BISHOPS_END_GAME / 100

        self.rooks_early_game: np.ndarray = ROOKS_EARLY_GAME / 100
        self.rooks_end_game: np.ndarray = ROOKS_END_GAME / 100

        self.queens_early_game: np.ndarray = QUEENS_EARLY_GAME / 100
        self.queens_end_game: np.ndarray = QUEENS_END_GAME / 100

        self.kings_early_game: np.ndarray = KINGS_EARLY_GAME / 100
        self.kings_end_game: np.ndarray = KINGS_END_GAME / 100

        # TODO: @schmitse ADD THOSE TABLES AND IMPLEMENT THEIR LOGIC
        # self.kingside_pawns_early_game: np.ndarray = KINGSIDEPAWNS_EARLY_GAME
        # self.kingside_pawns_end_game: np.ndarray = KINGSIDEPAWNS_END_GAME

        # self.queenside_pawns_early_game: np.ndarray = QUEENSIDEPAWNS_EARLY_GAME
        # self.queenside_pawns_end_game: np.ndarray = QUEENSIDEPAWNS_END_GAME

        return None

    @staticmethod
    def _scale(num_pieces) -> float:
        return 2 * (num_pieces - MIN_PIECES) / (MAX_PIECES - MIN_PIECES) - 1

    @staticmethod
    def game_state(num_pieces: int | float, width: float = 6.) -> float:
        return 1 / (np.exp(Evaluator._scale(num_pieces) * width) + 1)
    
    def __call__(self, state: chess.Board, color: bool) -> float:
        """ evaluate quality of position based on material and PST depending on the game state """
        # if we have won or lost return inf score, if we draw return 0
        if state.is_game_over():
            if state.outcome():
                return np.inf
            return 0
        # score initialised to be equal and subsequently built up from PST
        score: float = 0.0
        # measure for how far advanced the game state is and which 
        # piece square tables to use when evaluating the score. 
        game_state = self.game_state(state.pawns.bit_count() + state.knights.bit_count() 
                                     + state.bishops.bit_count() + state.rooks.bit_count()
                                     + state.queens.bit_count() + state.kings.bit_count())

        # scale the PST depending on the game state 
        pawns_map = self.pawns_early_game * (1 - game_state) + self.pawns_end_game * game_state + self.PAWN
        knights_map = self.knights_early_game * (1 - game_state) + self.knights_end_game * game_state + self.KNIGHT
        bishops_map = self.bishops_early_game * (1 - game_state) + self.bishops_end_game * game_state + self.BISHOP
        rooks_map = self.rooks_early_game * (1 - game_state) + self.rooks_end_game * game_state + self.ROOK
        queens_map = self.queens_early_game * (1 - game_state) + self.queens_end_game * game_state + self.QUEEN
        kings_map = self.kings_early_game * (1 - game_state) + self.kings_end_game * game_state + self.KING

        # get bitmap for your pieces on the board
        own_pawns = chess.SquareSet(state.pawns & state.occupied_co[color])
        own_knights = chess.SquareSet(state.knights & state.occupied_co[color])
        own_bishops = chess.SquareSet(state.bishops & state.occupied_co[color])
        own_rooks = chess.SquareSet(state.rooks & state.occupied_co[color])
        own_queens = chess.SquareSet(state.queens & state.occupied_co[color])
        own_kings = chess.SquareSet(state.kings & state.occupied_co[color])

        # sum up the piece values based on position 
        score_own_pawns = sum([pawns_map[square] for square in own_pawns])
        score_own_knights = sum([knights_map[square] for square in own_knights])
        score_own_bishops = sum([bishops_map[square] for square in own_bishops])
        score_own_rooks = sum([rooks_map[square] for square in own_rooks])
        score_own_queens = sum([queens_map[square] for square in own_queens])
        score_own_kings = sum([kings_map[square] for square in own_kings])
        score += (score_own_pawns + score_own_knights + score_own_bishops 
                  + score_own_rooks + score_own_queens + score_own_kings)

        # get bitmap for enemy pieces on the board, note the flip to account for the 
        # asymmetrical PSTs, which should be taken into account. 
        enemy_pawns = chess.SquareSet(chess.flip_vertical(state.pawns & state.occupied_co[not color]))
        enemy_knights = chess.SquareSet(chess.flip_vertical(state.knights & state.occupied_co[not color]))
        enemy_bishops = chess.SquareSet(chess.flip_vertical(state.bishops & state.occupied_co[not color]))
        enemy_rooks = chess.SquareSet(chess.flip_vertical(state.rooks & state.occupied_co[not color]))
        enemy_queens = chess.SquareSet(chess.flip_vertical(state.queens & state.occupied_co[not color]))
        enemy_kings = chess.SquareSet(chess.flip_vertical(state.kings & state.occupied_co[not color]))

        # sum up the piece values based on position 
        score_enemy_pawns = sum([pawns_map[square] for square in enemy_pawns])
        score_enemy_knights = sum([knights_map[square] for square in enemy_knights])
        score_enemy_bishops = sum([bishops_map[square] for square in enemy_bishops])
        score_enemy_rooks = sum([rooks_map[square] for square in enemy_rooks])
        score_enemy_queens = sum([queens_map[square] for square in enemy_queens])
        score_enemy_kings = sum([kings_map[square] for square in enemy_kings])
        score -= (score_enemy_pawns + score_enemy_knights + score_enemy_bishops 
                  + score_enemy_rooks + score_enemy_queens + score_enemy_kings)

        return score
    
