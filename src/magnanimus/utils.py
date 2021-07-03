from termcolor import cprint
import pandas as pd
import numpy as np

from .constants import REV_PIECE_CODES, INIT_BOARD_TUPLES


def make_board_df(piece_tuples=None):
    """
    Make a new style df - just for init
    """
    piece_tuples = piece_tuples or INIT_BOARD_TUPLES

    df = pd.DataFrame(piece_tuples)
    df.columns = ['piece', 'color', 'square']
    df = df.set_index('square')

    df[['free', 'attacking', 'defending']] = None
    # df[['free', 'attacking', 'defending']] = (
    #     df[['free', 'attacking', 'defending']].astype('object'))

    df['gives_check'] = False
    df['score'] = 0
    df['piece'] = df['piece'].astype('category')
    df['color'] = df['color'].astype('category')

    return df



def invert_color(color):
    if color == 'black':
        return 'white'
    return 'black'


