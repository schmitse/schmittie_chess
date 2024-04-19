from typing import Self
from ..config import const
from pygame.surface import Surface
from pygame.font import SysFont, Font
from .pieces import TextureHolder
from .mouse import Mover
from itertools import product
from numpy import unravel_index
import logging
import chess
import chess.pgn
import pygame
import io


class Board:
    """
    Game Board class that features the rendering of the pygame
    """
    _BLACK: tuple[int, int, int] = (135, 95, 60)
    _WHITE: tuple[int, int, int] = (255, 255, 200)
    
    def __init__(self, fen: str | None = None, folder: str = 'greenchess') -> None:
        """ Initialiser of Board instance
        Takes: 
            - fen: (optional str) the fen to start from
        """
        self.logger = logging.getLogger(__name__)

        if fen is None:
            self.board: chess.Board = chess.Board()
        else:
            self.board: chess.Board = chess.Board(fen=fen)
        self._pgn: dict[int, list[str]] = {}

        # - setup board rank and file annotations
        self.font: Font = SysFont('computermodern', 24)
        self.rank_letters: list = [self.font.render(f'{col + 1:.0f}', False, 'white') 
                                   for col in range(const.COLS)]
        self.file_letters: list = [self.font.render(_file, False, 'white') 
                                   for _file in const.FILENAMES]
        # - pieces with rendering information
        self.textures = TextureHolder(folder=folder)

        # - mover to generate the moves for the player
        self.mover = Mover()

    @classmethod
    def from_fen(cls, fen: str) -> Self:
        """make class from fen
        Takes:
            - fen : (str) the board fen to set. 
        """
        return cls(fen)
    
    @classmethod
    def from_pgn(cls, pgn: str) -> Self:
        game: chess.pgn.Game | None = chess.pgn.read_game(io.StringIO(pgn))
        if game is None:
            return cls()
        return cls(game.board().fen())
    
    def reset(self) -> None:
        """ reset the current board to the starting position """
        self.logger.debug('Resetting Board Position: ')
        self.board.reset()
        self._pgn.clear()
        self.logger.debug(f'FEN: {self.board.fen()}; PGN: {self._pgn}')
        return None

    def render_board(self, surface: Surface) -> None:
        """ render board on the game surface 
        Takes:
            - surface: (Surface) the game surface to render on
        """
        # - make brown edge around the board to display rank and file on
        surface.fill('#1e140a')
        # - offset due to the outside board
        offset: int | float = const.OFFSET
        for row, col in product(range(const.ROWS), range(const.COLS)):
            # - draw rectangle in cream or brown depending on row and col
            color: tuple[int, int, int] = self._BLACK if (row + col) % 2 else self._WHITE
            rect: tuple[int | float, int | float, int, int] = (offset + col * const.SQSIZE, offset + row * const.SQSIZE, const.SQSIZE, const.SQSIZE)
            pygame.draw.rect(surface, color, rect)

            # - draw rank and file annotations if at edge of the board
            if row == const.ROWS - 1:
                rank_rect: tuple[float, float, int, int] = (offset + (col + 0.475) * const.SQSIZE, offset + (row + 1.05) * const.SQSIZE, const.SQSIZE, const.SQSIZE)
                surface.blit(self.file_letters[col], rank_rect)
            if not col:
                file_rect: tuple[float, float, int, int] = (offset + (col - 0.15) * const.SQSIZE, offset + (row + 0.475) * const.SQSIZE, const.SQSIZE, const.SQSIZE)
                surface.blit(self.rank_letters[const.ROW_HASH[row]], file_rect) 
        return None

    def render_pieces(self, surface: Surface) -> None:
        """ render pieces on the game surface
        Takes:
            - surface: (Surface) the game surface to render on
        """
        # - offset to center pieces with board that has rim around it
        offset: int | float = const.OFFSET
        # - go through all pieces to place them on the board
        for piece_type, piece_color in product(const.PIECES, [const.WHITE, const.BLACK]):
            # - get square set for each piece type
            positions: chess.SquareSet = self.board.pieces(piece_type, piece_color)
            piece_name: str = chess.piece_name(piece_type)
            color: str = const.color(piece_color)
            # - iterate through set and position corresponding image
            for pos in positions:
                img: Surface = self.textures[f'{color}-{piece_name}']
                row, col = unravel_index(pos, (const.COLS, const.ROWS))
                center = (offset + (col + 0.5) * const.SQSIZE, offset + (const.ROW_HASH[row] + 0.5) * const.SQSIZE)
                surface.blit(img, img.get_rect(center=center))

    def render_legal_moves_with_piece(self, surface: Surface, color: str = '#013220', size: float = 0.1) -> None:
        """ renders the legal moves with the selected piece """
        if not self.mover.moving:
            return
        legal_moves_from_square: list[chess.Move] = [m for m in self.board.legal_moves if m.uci().startswith(self.mover.init_square_name)]
        target_squares: list[str] = [m.uci()[2:4] for m in legal_moves_from_square]
        for square in target_squares:
            row, col = [float(el) for el in unravel_index(chess.parse_square(square), (const.COLS, const.ROWS))]  # whacky for killing type error
            row = const.ROW_HASH[int(row)]
            center: tuple[float, float] = (const.OFFSET + (col + 0.5) * const.SQSIZE, const.OFFSET + (row + 0.5) * const.SQSIZE)
            radius: float | int = const.SQSIZE * size
            pygame.draw.circle(surface, color, center, radius)

    def check_user_legal_move(self, promotion: str = 'q') -> bool:
        """ checks if the selected mouse clicks are indeed legal moves. """
        mv: chess.Move | None = self.get_move(promotion)
        if mv is None:
            return False
        return mv in self.board.legal_moves
    
    def update(self, move: None | chess.Move) -> None:
        self.push(move)
        return None
    
    def get_move(self, promotion: str = 'q') -> chess.Move | None:
        """ get move, if promotion available choose queen by default. """
        move_uci = self.mover.init_square_name + self.mover.final_square_name
        moves = [mv for mv in self.board.legal_moves if mv.uci().startswith(move_uci)]
        if not len(moves):
            return None
        elif len(moves) > 1:
            return chess.Move.from_uci(move_uci + promotion)
        return moves[0]

    def push(self, move: chess.Move | None) -> None:
        """ push a move on the board """
        if move is None:
            return None
        if self.board.fullmove_number in self._pgn:
            self._pgn[self.board.fullmove_number].append(self.board.san(move))
        else:
            self._pgn[self.board.fullmove_number] = [self.board.san(move)]
        self.board.push(move)

    def undo_last_move(self) -> None:
        """ undo the last move made """
        self.logger.warning(self.board.ply())
        if not self.board.ply():
            return None
        mvnumber = self.board.fullmove_number - 1 if self.board.turn else self.board.fullmove_number
        self.logger.warning(mvnumber)
        self.board.pop()
        self._pgn[mvnumber].pop()
        if self._pgn[mvnumber]:
            return None
        self._pgn.pop(mvnumber)
        return None

    def pgn(self) -> str:
        return ' '.join([f'{k}. {" ".join(it)}' for k, it in self._pgn.items()]) + f' {self.board.result()}'
