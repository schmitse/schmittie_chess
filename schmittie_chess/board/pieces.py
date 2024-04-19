from ..config import const
from itertools import product
import chess
import pygame
import os
import logging


class TextureHolder():
    def __init__(self, folder: str = 'greenchess') -> None:
        self.logger = logging.getLogger(__name__)
        self.folder: str = folder
        piece_names = [chess.piece_name(piece) for piece in const.PIECES]
        colors = [const.WHITE, const.BLACK]
        self.logger.debug(f'Loading the pictures from {folder} folder.')
        self.textures = {f'{const.color(color)}-{name}': pygame.image.load(get_texture(name, color, folder)) 
                         for name, color in product(piece_names, colors)}
        self.textures = {key: pygame.transform.scale(item, (const.SQSIZE * 0.95, const.SQSIZE * 0.95)) 
                         for key, item in self.textures.items()}

    def __getitem__(self, key: str | int | float) -> pygame.Surface:
        if key in self.textures:
            return self.textures[key]
        raise KeyError(f'Invalid Key for texture holder: {key}')


def get_texture(name: str, color: bool, folder: str = 'greenchess') -> str:
    """ get texture path for given piece, color, and folder 
    Takes:
        - name: (str) the name of the piece
        - color: (bool) the color of the piece
        - folder: (str) the folder to look up
    """
    _color = 'white' if color else 'black'
    _dir: str = os.path.dirname(__file__)
    texture: str = os.path.join(_dir, 'pictures', folder, f'{_color}-{name.lower()}.png')
    if not os.path.exists(texture):
        raise FileNotFoundError(f'The File {texture} does not exist!')
    return texture