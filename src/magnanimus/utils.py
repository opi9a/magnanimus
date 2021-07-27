from termcolor import cprint
import pandas as pd
import numpy as np

from .constants import REV_PIECE_CODES, INIT_BOARD_TUPLES
from .notation import trad_to_int


def make_board_df(piece_seed=None):
    """
    Make an empty board df (no analysis)
    """
    if isinstance(piece_seed, str):
        piece_tuples = piece_tuples_from_str(piece_seed)

    elif piece_seed is None:
        piece_tuples = INIT_BOARD_TUPLES

    else:
        piece_tuples = piece_seed

    df = pd.DataFrame(piece_tuples)
    df.columns = ['piece', 'color', 'square']
    df = df.set_index('square')

    df[['free', 'attacking', 'just_covering', 'defending']] = None

    df['gives_check'] = False
    df['score'] = 0.0
    df['piece'] = df['piece'].astype('category')
    df['color'] = df['color'].astype('category')

    return df



def invert_color(color):
    if color == 'black':
        return 'white'
    return 'black'


def piece_tuples_from_str(board_str):
    """
    Make a df from string such as:
        "ke8 Ke6 Qa1"
    """
    piece_strs = board_str.split()

    out = []

    for piece_str in piece_strs:

        if piece_str[0].islower():
            color = 'black'
        else:
            color = 'white'

        piece = REV_PIECE_CODES[piece_str[0].lower()]

        sq_str = piece_str[1:]

        if sq_str.isnumeric():
            sq = int(sq_str)
        else:
            sq = trad_to_int(sq_str)

        out.append((piece, color, sq))

    return out  


