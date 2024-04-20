from typing import Callable
import chess
from chess import BB_KNIGHT_ATTACKS, BB_FILE_ATTACKS, BB_DIAG_ATTACKS, BB_PAWN_ATTACKS, BB_DIAG_MASKS, BB_FILE_MASKS, BB_ALL, SquareSet, Square

popcount: Callable[[int], int] = getattr(int, "bit_count", lambda bb: bin(bb).count("1"))


def gives_check(move: chess.Move, board: chess.Board) -> bool:
    """ checking whether or not a given move would put the opposing king into check using bitboards """
    # get target square, piece type and king position
    target_square: Square = move.to_square
    piece_type: chess.PieceType | None = board.piece_type_at(move.from_square)
    if piece_type is None:
        return False
    king_square: Square | None = board.king(not board.turn)
    if king_square is None:
        return False

    # prepare masks for attacking style of moved piece
    true: SquareSet = SquareSet(BB_ALL)
    false: SquareSet = SquareSet(0)
    match piece_type:
        case chess.PAWN:
            knight_like: SquareSet = false
            diag_like: SquareSet = false
            file_like: SquareSet = false
            pawn_like: SquareSet = true
        case chess.KNIGHT:
            knight_like: SquareSet = true
            diag_like: SquareSet = false
            file_like: SquareSet = false
            pawn_like: SquareSet = false
        case chess.BISHOP:
            knight_like: SquareSet = false
            diag_like: SquareSet = true
            file_like: SquareSet = false
            pawn_like: SquareSet = false
        case chess.ROOK:
            knight_like: SquareSet = false
            diag_like: SquareSet = false
            file_like: SquareSet = true
            pawn_like: SquareSet = false
        case chess.QUEEN:
            knight_like: SquareSet = false
            diag_like: SquareSet = true
            file_like: SquareSet = true
            pawn_like: SquareSet = false
        case chess.KING:
            return False
        case _:
            return False

    # combine different attack bitboards into one "places from which to check king bitboard"
    pawn_attacks: SquareSet = SquareSet(BB_PAWN_ATTACKS[board.turn][king_square]) & pawn_like
    knight_attacks: SquareSet = SquareSet(BB_KNIGHT_ATTACKS[king_square]) & knight_like
    diag_attacks: SquareSet = SquareSet(BB_DIAG_ATTACKS[king_square][BB_DIAG_MASKS[king_square] & board.occupied])
    file_attacks: SquareSet = SquareSet(BB_FILE_ATTACKS[king_square][BB_FILE_MASKS[king_square] & board.occupied])
    king_visibility: SquareSet = ~SquareSet(board.occupied) & (knight_attacks | diag_attacks | file_attacks | pawn_attacks)

    # check if the target square bitboard is in the "places from which to check king bitboard"
    target_set = chess.SquareSet([target_square])
    return bool(target_set & king_visibility)