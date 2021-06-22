import numpy as np
import pandas as pd

from .utils import invert_color

"""
Position:
    board:
        matrix of squares (np array - or just dict with (row, col) keys?)
        each square has a piece object or None
    pieces:
        list of pieces
    scores:
        white / black

Raw Domains (constant):
    board shaped matrix with, at each square:
        - a list of reachable squares (on an empty board) for each piece type:
        - for rook, bishop, queen there is a list of lists, each of which
          contains the spaces reached in a different direction, in order from
          the root square
        - for king, knight just a flat list
        - for pawn, separate lists for moving (fwd 1 or 2) and hitting (diag)

Piece:
    name, color, square
    available spaces - reachable by the piece
    defended spaces - same color pieces
    attacked spaces - opp color pieces
    score

Position:
    overall score (for each side), given:
        - piece strengths
        (are the below different to that?)
        - check 
        - threats / threatened

Move:
    update board (old.square = none, new = the piece)
    update piece:
        position
        domains
        score
    update other affected pieces:
        incrementally or just rescan board
    calc scores

Choice:
    Simulate moves
    Assess positions
    Select top N moves
    Simulate and repeat
"""
from .constants import INIT_BOARD_TUPLES, BASE_COLS, LOG
from .utils import (trad_from_vec, vec_from_trad, print_board,
                    expand_color, expand_piece)
from .Piece import Piece
from .domains import make_domains

# get the empty-board domains (by square, by piece)
RAW_DOMAINS = make_domains()

def analyse_board(board_arr, to_move):
    """
    For an array of (<color>, <piece>), return score info and possible
    next moves for the passed color

    Do this by making a Piece object at each square that's not None,
    and recording its info
    """

    piece_data = []
    moves = []
    for row in range(8):
        for col in range(8):

            if board_arr[row, col] is None:
                continue

            piece = Piece(board_arr, row, col)

            piece_data.append([piece.name, piece.color,
                               *piece.square, piece.score, piece.gives_check])

            if piece.next_moves and piece.color == to_move:
                for move in piece.next_moves:
                    moves.append({
                        'from': (row, col),
                        'to': move,
                    })


    df = pd.DataFrame(piece_data, columns=BASE_COLS + ['score', 'gives_check'])
    df = df.sort_values(['color'], ascending=False)

    scores = dict(df.groupby('color')['score'].sum())
    for color in ['white', 'black']:
        if color not in scores: scores[color] = 0
    net_score = round(scores['white'] - scores['black'], 3)
    moves = pd.DataFrame(moves).values

    if df['gives_check'].any():
        checks = df.loc[df['gives_check'], 'color'].unique()
        # assert len(in_check) == 1
        is_checked = invert_color(checks[0])
    else:
        is_checked = None

    return scores, net_score, moves, is_checked
