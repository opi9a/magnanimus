"""
Extending paths:
Take a paths list / json and return an extended version.

paths = [
    {
        'path': [(14, 22)],
        'score': 0.4,
        'last_to_move': 'black',
        'df': <board_df>,
        'next_to_move': 'white',
        'next_moves': [(50, 34), (50, 42), ..],
},
    {
        'path': [(14, 30)],
        'score': -0.4,
        'last_to_move': 'black',
        'df': <board_df>,
        'next_to_move': 'white',
        'next_moves': [(50, 34), (50, 42), ..],
},
...
]

new_paths = [
    {
        'path': [(14, 22), (50, 34)],
        'score': 1.4,
        'last_to_move': 'white',
        'df': <board_df>,
        'next_to_move': 'black',
        'next_moves': [(10, 18), ..],
},
    {
        'path': [(14, 22), (50, 42)],
        'score': 3.5,
        'last_to_move': 'white',
        'df': <board_df>,
        'next_to_move': 'black',
        'next_moves': [(10, 18),  ..],
},
...
]

For each path:
    for each next_move:
        make a new df
        get score and new moves

"""

import pandas as pd
from datetime import datetime, timedelta

from .constants import LOG
from .utils import invert_color
from .analyse import analyse_board
from .scoring import CHECKMATE_SCORE, STALEMATE_SCORE
from .Path import Path

def get_best_move(df, to_move, max_its=2, return_paths=False):
    """
    For passed df:
        init paths json object
        extend paths
        return best
    """

    # make sure the df is elaborated
    df = analyse_board(df)

    # init the paths list
    paths = [Path(df=df, to_move=to_move)]

    its = 0
    while its < max_its:
        print(f'getting paths for it {its}, with {to_move} to move')
        paths = extend_paths(paths, to_move)
        to_move = invert_color(to_move)
        its += 1


    paths.sort(key=lambda x: x.score)

    if to_move == 'white':
        best_move = paths[0].moves[0]
    else:
        best_move = paths[-1].moves[0]

    if return_paths:
        return best_move, paths

    return best_move


def extend_paths(paths, timeout=None, sec_to_think=1,
                 npaths_to_follow=5):
    """
    Return a list of paths that extend the one passed.
    Identify mates
    """

    if timeout is None:
        timeout = datetime.now() + timedelta(seconds=sec_to_think)

    paths_out = []

    # iterate over each existing path, spawning new ones from its next_moves
    for i,path in enumerate(paths):

        if path.mate:
            paths_out.append(path)
            continue

        # collect the new paths from this path, before deciding
        # whether to append to the main list
        child_paths = []

        # helpful later to know if they started off in check
        if path.to_move == path.checked:
            already_in_check = True
        else:
            already_in_check = False

        print(f'extending path {i+1} / {len(paths)}, {path.to_move} to move,'
              f' {"they ARE" if path.checked else "NOT"} in check')
        for move in path.next_moves:
            new_path = Path(path, move)
            # need to get who is checked
            # if its last_to_move, reject
            if new_path.checked == path.to_move:
                print(f'dropping {move}: self check for {path.to_move}')
                # not a legit move
                continue
            else:
                child_paths.append(new_path)

        if not child_paths:
            # no options so mate of some kind
            # -> append a mated path
            if already_in_check:
                # mate for the opponent
                path.score = CHECKMATE_SCORE * (
                    -1 if path.to_move == 'black' else 1)
            else:
                # stalemate
                path.score = STALEMATE_SCORE

            path.next_moves = None
            path.mate = True
            paths_out.append(path)

        else:
            paths_out.extend(child_paths)

    # TODO select paths to follow

    return paths_out


