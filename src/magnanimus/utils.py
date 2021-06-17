from termcolor import cprint
import pandas as pd
import numpy as np

from .constants import (
    PIECE_UNICODES, REV_PIECE_CODES, BASE_COLS, INIT_BOARD_TUPLES
)

from .Piece import Piece


def invert_color(color):
    if color == 'black':
        return 'white'
    return 'black'

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

def update_board(board_arr, moves):
    """
    Working on board_arr, return a board with the move made
    """

    # todo ensure moves is a list of moves, not a single move

    out = board_arr.copy()
    for move in moves:
        sq_from, sq_to = move
        out[sq_to] = out[sq_from]
        out[sq_from] = None

    return out



def board_to_str(board_arr):
    out = []
    for row in range(8):
        for col in range(8):
            pass


def get_board_str(board_arr=None, board_tuples=None, 
                scores=None, hlights=None):
    """
    Return a board_arr string representation
    """

    if board_arr is None:
        board_arr = make_board_from_tuples(board_tuples)

    out = []
    
    if scores is not None:
        out.append('    Black:', f"{scores['black']:.3f}")

    black = False

    col_line = ["    "]
    for col in range(8):
        col_line.append(f" {col} ")
    out.append("".join(col_line))

    row_names = range(1, 9)[::-1] # for trad notation
    for row in range(8):
        row_line = [f" {row}  "]
        for col in range(8):

            if board_arr is None:
                to_print = f"{row},{col}"
            elif board_arr[row, col] is None:
                to_print = ("\u00B7")
            else:
                color, p_name = board_arr[row, col]
                to_print = (f"{PIECE_UNICODES[color][p_name]}")

            if hlights is not None and (row, col) in hlights:
                row_line.append(f"|{to_print}|")
            elif board_arr is not None:
                row_line.append(f" {to_print} ")
        out.append("".join(row_line))


    return "\n".join(out)


def print_board(board_arr=None, board_tuples=None, 
                scores=None, hlights=None):
    """
    Print the passed board array.
    Trad notation on west / south axes, np.array notation on north / east

    pass a list of squares to hlights and they will be identified with | |
    """

    if board_arr is None:
        board_arr = make_board_from_tuples(board_tuples)

    print()
    
    if scores is not None: print('    Black:', f"{scores['black']:.3f}")

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
    if scores is not None: print('    White:', f"{scores['white']:.3f}")



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
