# - the players that are currently implemented: 
from .player import BasePlayer, HumanPlayer, TheFish
from .player_minimax import PlayerMiniMax
from .player_dev import PlayerDev
from .player_dev import MoveHandler
from .player_minimax import generate_legal_moves
from .evaluation import Evaluator