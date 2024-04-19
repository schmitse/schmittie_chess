from dataclasses import dataclass, field
from numpy import array


@dataclass
class Const:
    HEIGHT: int = 850
    TIMEMARGIN: int = 50
    _RIM : int = 50
    COLS: int = 8
    SQSIZE: int = (HEIGHT - _RIM) // COLS
    WIDTH = HEIGHT + TIMEMARGIN + 2 * SQSIZE
    ROWS = COLS
    FILENAMES: list[str] = field(default_factory=lambda: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])
    OFFSET: int | float = (HEIGHT - SQSIZE * ROWS) / 2
    WHITE: bool = True
    BLACK: bool = False
    PIECES: list[int] = field(default_factory=lambda: list(range(1, 7)))
    VALUE_HASH: dict[int, float] = field(default_factory=lambda: {1: 1, 2: 2.8, 3: 3.1, 4: 5, 5: 9, 6: 100000})

    def __post_init__(self):
        self.EDGES = array([self.OFFSET + j * self.SQSIZE for j in range(self.COLS + 1)])
        self.ROW_HASH: dict[int, int] = {0: 7, 1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1, 7: 0}
        self.ROW_INV: dict[str, str] = {'1': '8', '2': '7', '3': '6', '4': '5', 
                                        '5': '4', '6': '3', '7': '2', '8': '1'}
        self.FILE_INV: dict[str, str] = {'a': 'h', 'b': 'g', 'c': 'f', 'd': 'e', 
                                         'e': 'd', 'f': 'c', 'g': 'b', 'h': 'a'}

    def color(self, color: bool) -> str:
        if color:
            return 'white'
        return 'black'

const = Const()
