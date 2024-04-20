from chess import Board, Outcome
from schmittie_chess.players import PlayerMiniMax, PlayerDev
from io import StringIO
from chess.pgn import read_game
import time
import logging


class ComputerPlay:
    def __init__(self, player_white, player_black, fen: str | None = None, name: str | None = None, 
                 white_kwargs: dict | None = None, black_kwargs: dict | None = None) -> None:
        self.logger = logging.getLogger(__name__ if name is None else name)
        if fen is None:
            self.board = Board()
        else:
            self.board = Board(fen=fen)
        _white_kwargs: dict = {} if white_kwargs is None else white_kwargs
        _black_kwargs: dict = {} if black_kwargs is None else black_kwargs
        self.player_white = player_white(color=True, **_white_kwargs)
        self.player_black = player_black(color=False, **_black_kwargs)
        self.moves: dict[int, list[str]] = {}
        self.games: list[str] = []
        self.results: list = []
        self.times: dict[float] = {}
        return None
    
    def set_fen(self, fen: str) -> None:
        self.board = Board(fen)
        self.moves.clear()
        self.times.clear()
        return None
    
    def set_pgn(self, pgn: str) -> None:
        self.moves.clear()
        self.times.clear()
        self.board = Board()
        pgn_string: StringIO = StringIO(pgn)
        game = read_game(pgn_string)
        if game is None:
            raise ValueError(f'Could not parse pgn: {pgn}')
        for move in game.mainline_moves():
            if self.board.turn:
                self.moves[self.board.fullmove_number] = [self.board.san(move)]
                self.times[self.board.fullmove_number] = [-1]
            else:
                self.moves[self.board.fullmove_number].append(self.board.san(move))
                self.times[self.board.fullmove_number].append(-1)
            self.board.push(move)
        return None
    
    def pgn(self) -> str:
        return ' '.join([f'{k}. {" ".join(it)}' for k, it in self.moves.items()]) + f' {self.board.result()}'

    def time(self) -> str:
        return ' '.join([f'{k}. {" ".join(it)}' for k, it in self.times.items()]) + f' {self.board.result()}'

    def winner(self) -> int:
        winner_table = {True: 1, False: -1, None: 0}
        outcome = self.board.outcome()
        if outcome is None:
            return -2
        return winner_table[outcome.winner]
    
    def rollout(self) -> Outcome | None:
        self.logger.debug(self.board)
        while self.board.outcome() is None:
            move_time_0: float = time.perf_counter()
            if self.board.turn:
                move = self.player_white.choose_move(self.board.copy(), 10000, depth=4)
                self.moves[self.board.fullmove_number] = [self.board.san(move)]
                move_time_1: float = time.perf_counter()
                self.times[self.board.fullmove_number] = [move_time_1 - move_time_0]
            else:
                move = self.player_black.choose_move(self.board.copy(), 10000, depth=4)
                self.moves[self.board.fullmove_number].append(self.board.san(move))
                move_time_1: float = time.perf_counter()
                self.times[self.board.fullmove_number].append(move_time_1 - move_time_0)
            self.board.push(move)
        self.games.append(self.pgn())
        self.results.append(self.board.outcome())
        return self.board.outcome()
    
    def __repr__(self) -> str:
        return f'ComputerPlay(player_white={repr(self.player_white)}, player_black={repr(self.player_black)})'
    
    def __str__(self) -> str:
        wins_white: int = sum([1 for outcome in self.results if outcome.winner])
        draws: int = sum([1 for outcome in self.results if outcome.winner is None])
        wins_black: int = len(self.games) - wins_white - draws
        total_games = len(self.games)
        win_string: str = (f'Wins white: {(wins_white / total_games) * 100:.2f}% ({wins_white:.0f}) \n'
                           + f'Wins black: {(wins_black / total_games) * 100:.2f}% ({wins_black:.0f}) \n'
                           + f'Draws: {(draws / total_games) * 100:.2f}% ({draws:.0f})')
        return "\n".join(self.games) + '\n' + win_string