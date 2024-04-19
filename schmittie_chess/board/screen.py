from ..config import const
from .board import Board
from ..players.player import HumanPlayer, BasePlayer, TheFish
from ..players.player_minimax import PlayerMiniMax
from datetime import timedelta
from chess import Move
import pygame
import logging
import time


class Game:
    """
    Game Class which runs the main loop of python chess
    """
    def __init__(self, folder: str = 'greenchess', verbosity: int = logging.DEBUG, increment: int = 0) -> None:
        """ initialiser for the Game instance """
        pygame.init()
        logging.basicConfig(level=verbosity)
        self.logger = logging.getLogger(__name__)
        self.screen = pygame.display.set_mode((const.WIDTH, const.HEIGHT))
        self.clock = pygame.time.Clock()
        self.board = Board(folder=folder)
        self.running = True

        self.time_white: int = 10 * 60 * 1000
        self.time_black: int = 10 * 60 * 1000
        self.move_times: dict[bool, list[int]] = {True: [], False: []}
        self.increment: int = increment
        self.timefont: pygame.font.Font = pygame.font.SysFont('computermodern', 80, bold=True)

        # self.players = {False: HumanPlayer(color=False), True: PlayerMiniMax(color=True)} # BasePlayer(color=False)}  # TheFish(color=False)}
        self.players = {True: HumanPlayer(color=True), False: PlayerMiniMax(color=False)} # BasePlayer(color=False)}  # TheFish(color=False)}
        return None
    
    def mainloop(self) -> None:
        """ main loop of the game UI """
        mv_time: int = 0
        move: None | Move = None
        t0 = time.time()
        while self.running:
            self.clock.tick()
            self.board.render_board(self.screen)
            self.board.render_pieces(self.screen)
            self.board.render_legal_moves_with_piece(self.screen)
            self._render_time()

            if self.board.board.is_game_over():
                self.running = False
                self._finalise_game()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self._finalise()
                    break

                if not self.players[self.board.board.turn].auto:
                    mv_time, move = self._handle_mouse_input(event, mv_time)
                self._handle_keyboard_events(event)

            if self.players[self.board.board.turn].auto:
                move = self._handle_computer_player()
            t1 = time.time()
            ctime = int((t1 - t0) * 1000)
            mv_time += ctime
            if self.board.board.turn:
                self.time_white -= ctime
                self.running = self.time_white > 0
            else:
                self.time_black -= ctime
                self.running = self.time_black > 0
            move = self.board.update(move)

            pygame.display.flip()
            t0 = time.time()
        self._finalise()
        return None
    
    def _handle_keyboard_events(self, event: pygame.event.Event) -> None:
        """ handles various different key presses """
        if event.type != pygame.KEYDOWN:
            return None
        match event.key:
            case pygame.K_r:
                self.logger.debug('Button R was pressed: Resetting Board Position.')
                self.board.reset()
                self.time_white: int = 10 * 60 * 1000
                self.time_black: int = 10 * 60 * 1000
            case pygame.K_b:
                self.logger.debug('Button B was pressed: Reverting last move.')
                self.board.undo_last_move()
            case _:
                self.logger.error('Unknown Button pressed')

    def _handle_computer_player(self) -> Move:
        turn: bool = self.board.board.turn
        player: BasePlayer = self.players[turn]
        t0 = time.time()
        move: Move = player.choose_move(self.board.board.copy(), self.time_white if turn else self.time_black)
        t1 = time.time()
        # self.board.push(move)
        self.move_times[turn].append(int((t1 - t0) * 1000))
        return move

    def _handle_mouse_input(self, event: pygame.event.Event, mv_time) -> tuple[int, None | Move]:
        match event.type:
            case pygame.MOUSEBUTTONDOWN:
                self.board.mover.get_initial_position(event.pos)
                piece = self.board.board.piece_at(self.board.mover.init_square)
                if piece is None:
                    return mv_time, None
                self.logger.debug(f'Selected piece: {piece = } at {self.board.mover.init_square_name}')
                return mv_time, None

            case pygame.MOUSEBUTTONUP:
                self.board.mover.get_final_position(event.pos)
                self.logger.debug(f'Selected square: {self.board.mover.final_square_name}')

                if not self.board.check_user_legal_move():
                    self.logger.error('Move was not legal, continuing')
                    return mv_time, None
                move = self.board.get_move()
                if move is None:
                    self.logger.error(f'Move is None which it shouldnt!')
                    self.logger.error(f'{self.board.mover}')
                    self.logger.error(self.board.board)
                    return mv_time, None
                self.move_times[self.board.board.turn].append(mv_time)
                if self.board.board.turn:
                    self.time_white += self.increment
                else:
                    self.time_black += self.increment
                self.logger.debug(f'Move time: {mv_time / 1000:.2f}s Remaining: {self.time_white / 1000:.2f} {self.time_black / 1000:.2f}')
                mv_time = 0
                # self.board.push(move)
                return mv_time, move
        return mv_time, None

    def _render_time(self) -> None:
        """ renders clocks """
        tw = timedelta(milliseconds=self.time_white)
        tb = timedelta(milliseconds=self.time_black)
        time_white = self.timefont.render(str(tw).split('.')[0], False, '#c3c3c3')
        time_black = self.timefont.render(str(tb).split('.')[0], False, '#B5B2B3')
        pos_white = (const.OFFSET + const.SQSIZE * const.COLS + const.TIMEMARGIN, const.OFFSET + const.SQSIZE * (const.ROWS / 2 + 1), const.SQSIZE * 2, const.SQSIZE)
        pos_black = (const.OFFSET + const.SQSIZE * const.COLS + const.TIMEMARGIN, const.OFFSET + const.SQSIZE * (const.ROWS / 2 - 1), const.SQSIZE * 2, const.SQSIZE)
        self.screen.blit(time_white, pos_white)
        self.screen.blit(time_black, pos_black)
        return None

    def _finalise_game(self) -> None:
        self.logger.info('PGN for played game: ')
        self.logger.info(self.board.pgn())
        self.logger.info('')
        return None

    def _finalise(self) -> None:
        self._finalise_game()
        pygame.quit()
        return None




# def main() -> None:
#     folder = 'greenchess'  # 'funkey'
#     game = Game(folder=folder)
#     game.mainloop()
#     return None


# if __name__ == '__main__':
#     main()

