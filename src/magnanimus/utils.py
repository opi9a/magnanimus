from termcolor import cprint
import pandas as pd
import numpy as np

from .constants import (
    PIECE_UNICODES, REV_PIECE_CODES, BASE_COLS, INIT_BOARD_TUPLES
)

from .Piece import Piece


def test_print():
    print('\u2654')
    x = '\u2654'
    print(x)
    print(f"{x}")
    print(PIECE_UNICODES['white']['king'])

def make_board_from_tuples(piece_tuples):
    """
    From a list of piece tuples make a np array for board
    with K / k, Q / q etc

    This is the main encoding of the board
    """
    board_arr = np.array([None]*64).reshape(8,8)

    for pc, color, row, col in piece_tuples:
        board_arr[row, col] = color, pc

    return board_arr



def make_board(piece_tuples=None, file_path=None):
    """
    Return an np array representing the board, with piece objects
    Probably obsolete
    """

    # prepare inputs
    if file_path is not None:
        df = pd.read_csv(file_path)
        
        if 'trad_square' in df.columns and not(
            'row' in df.columns and 'col' in df.columns
        ):
            df['row'], df['col'] = zip(*df['trad_square'].apply(vec_from_trad))

    else:
        if piece_tuples is None:
            piece_tuples = INIT_BOARD_TUPLES

        df = pd.DataFrame(piece_tuples, columns=BASE_COLS)

    if df['color'].apply(len).max() == 1:
        df['color'] = df['color'].apply(expand_color)

    if df['piece'].apply(len).max() == 1:
        df['piece'] = df['piece'].apply(expand_piece)

    # an empty board
    board_arr = np.array([None]*64).reshape(8, 8)

    # place the pieces
    for i in df.index:
        board_arr[df.loc[i]['row'], df.loc[i]['col']] = Piece(
            name = df.loc[i]['piece'],
            color = df.loc[i]['color'],
            row = df.loc[i]['row'],
            col = df.loc[i]['col'],
            board_arr=None,
        )

    # now pieces in place calculate their domains and scores
    for row in range(8):
        for col in range(8):
            if board_arr[row, col] is not None:
                board_arr[row, col].calculate(board_arr)

    return board_arr




def print_board(board_arr=None, board_tuples=None, 
                scores=None, to_move=None, hlights=None):
    """
    Print the passed board array.
    Trad notation on west / south axes, np.array notation on north / east

    pass a list of squares to hlights and they will be identified with | |
    """

    if board_arr is None:
        board_arr = make_board_from_tuples(board_tuples)

    print()
    
    if scores is not None: 
        attrs = {'bold'} if to_move == 'black' else None
        cprint('    Black:', attrs=attrs, end="")
        print(f"{scores['black']:.3f}")

    black = False
    print("    ", end="")
    for col in range(8):
        print(f" {col} ", end=" ")
    print()

    row_names = range(1, 9)[::-1] # for trad notation
    for row in range(8):
        print(f" {row}  ", end="")
        for col in range(8):
            if board_arr is None:
                to_print = f"{row},{col}"
            elif board_arr[row, col] is None:
                to_print = (" ")
            else:
                color, p_name = board_arr[row, col]
                to_print = (f"{PIECE_UNICODES[color][p_name]}")

            if hlights is not None and (row, col) in hlights:
                to_print = f"|{to_print}|"
            elif board_arr is not None:
                to_print = f" {to_print} "

            if black:
                cprint(to_print, on_color='on_white', attrs={'bold'}, end=" ")
                black = False
            else:
                cprint(to_print, attrs={'bold'}, end=" ")
                black = True

            if col == 7:
                black = not(black)
        print(f" {row_names[row]}  ")

    print('    ', end="")
    for col in 'abcdefgh':
        print(f" {col} ", end=" ")
    print()
    if scores is not None: 
        attrs = {'bold'} if to_move == 'white' else None
        cprint('    White:', attrs=attrs, end="")
        print(f"{scores['white']:.3f}")



def vec_from_trad(trad):
    """
    Return an np.array vector of coordinates for a passed trad notation
    position.

    >>> vec_from_trad('a7')
    1, 0
    """
    file, rank = trad
    row = 8 - int(rank)
    col = 'abcdefgh'.find(file)

    return row, col


def trad_from_vec(*vec):
    """
    Return trad notation version of passed np.array coordinates

    >>> trad_from_vec(1, 0)
    'a7'
    """
    row, col = vec
    rank = 8 - row
    file = 'abcdefgh'[col]

    return f"{file}{rank}"


def expand_color(color_init):
    if color_init.lower() == 'w':
        return 'white'
    elif color_init.lower() == 'b':
        return 'black'
    else:
        raise ValueError(f'cannot expand color {color_init}')

def expand_piece(piece_init):
    return REV_PIECE_CODES[piece_init.lower()]
