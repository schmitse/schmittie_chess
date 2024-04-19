from ..config import const
from numpy import digitize
import logging
import chess


class Mover:
    """ class that moves the chess pieces across the board """
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.pos = (0., 0.)
        self.init_square: int = -1
        self.final_square: int = -1
        self.offset = const.OFFSET
        self.moving = False
        self.init_square_name: str = 'a1'
        self.final_square_name: str = 'a1'
        return None
    
    def get_initial_position(self, pos: tuple[float, float]) -> None:
        self.pos = pos
        self.init_square = self._get_square_from_pos(pos) 
        self.init_square_name = chess.square_name(self.init_square)
        self.logger.debug(f'-initial position- Updated Mouse Position to: {pos = } which is in {self.init_square = } with label {chess.square_name(self.init_square)}')
        self.moving = True
        return None
    
    def get_final_position(self, pos: tuple[float, float]) -> None:
        self.pos = pos
        self.final_square = self._get_square_from_pos(pos)
        self.final_square_name = chess.square_name(self.final_square)
        self.logger.debug(f'-final position- Updated Mouse Position to  {pos = } which is in {self.final_square = } with label {chess.square_name(self.final_square)}')
        self.moving = False
        return None
    
    @staticmethod
    def _get_square_from_pos(pos: tuple[float, float]) -> int:
        _square = digitize(pos, const.EDGES)
        return const.ROW_HASH[(_square[1] - 1)] * const.ROWS + _square[0] - 1

