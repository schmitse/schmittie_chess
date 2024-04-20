import os
import ray
from schmittie_chess.computer_play import ComputerPlay
from schmittie_chess.players import PlayerDev, PlayerMiniMax
import time
import chess


@ray.remote
def rollout(pgn: str, mode: int) -> tuple[int, str]:
    if mode:
        player_white = PlayerDev
        player_black = PlayerMiniMax
    else:
        player_white = PlayerMiniMax
        player_black = PlayerDev
    computer_play = ComputerPlay(player_white, player_black)
    computer_play.set_pgn(pgn)
    computer_play.rollout()
    return computer_play.winner(), computer_play.pgn()


def main() -> None:
    ray.init(num_cpus=6)

    with open(os.path.join('computer_play', 'openings.txt'), 'r') as fr:
        pgns = [line.strip('\n') for line in fr.readlines()]

    mode_one_res = [rollout.remote(pgn, 1) for pgn in pgns]
    mode_one_res = ray.get(mode_one_res)
    print('Finished Mode 1 Rollouts')
    mode_zero_res = [rollout.remote(pgn, 0) for pgn in pgns]
    mode_zero_res = ray.get(mode_zero_res)
    print('Finished Mode 0 Rollouts')

    ntot = len(mode_one_res) + len(mode_zero_res)
    dev_wins = (sum([1 for x in mode_one_res if x[0] == 1]) 
                + sum([1 for x in mode_zero_res if x[0] == -1])) 
    mini_wins = (sum([1 for x in mode_one_res if x[0] == -1]) 
                 + sum([1 for x in mode_zero_res if x[0] == 1]))
    draws = ntot - dev_wins - mini_wins
    print('Finished the games: PGNs')
    for _, pgn in mode_one_res:
        print(pgn)
    for _, pgn in mode_zero_res:
        print(pgn)
    
    print(f'Total Number of Games Played: {ntot:.0f}')
    print(f'PlayerDev wins:     {dev_wins / ntot * 100:.2f} ({dev_wins:.0f})')
    print(f'PlayerMiniMax wins: {mini_wins / ntot * 100:.2f} ({mini_wins:.0f})')
    print(f'Draws:              {draws / ntot * 100:.2f} ({draws:.0f})')
    return None


if __name__ == '__main__':
    main()