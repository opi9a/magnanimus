import pandas as pd
import numpy as np

from .domains import RAW_DOMAINS
from .scoring import COEFFS, PIECE_BASE_VALUES
from .notation import vec_to_int_sq

def analyse_board(df, squares=None):
    """
    Generate score, gives_check and next_moves for whole board or
    for an iterable of squares
    """

    df = df.copy()
    df[['free', 'attacking', 'defending']] = (
        df[['free', 'attacking', 'defending']].astype('object'))
    squares = squares or df.index

    for square in squares:
        free, attacking, defending, gives_check, score = (
            analyse_piece(square, df)
        )
        df.at[square, 'free'] = free 
        df.at[square, 'attacking'] = attacking 
        df.at[square, 'defending'] = defending 
        df.loc[square, ['gives_check', 'score']] = gives_check, score

    return df


def analyse_piece(square, df):
    """
    THIS IS WHAT NEEDED
    Take the row identified by square (pd.Series), and the df
    In situ set score, next_moves, gives check
    YOU ARE HERE:
        make this work on a single row / piece
        return the score and check, and do the union to get next_moves,
            so don't have to later
    """

    free, attacking, defending = get_piece_domains(square, df)

    # scoring
    base = PIECE_BASE_VALUES[df.loc[square, 'piece']]
    scores = { 'free': 0, 'attack': 0, 'defend': 0, 'checks': 0}

    # free may be a nested list, so flatten (row, col for each)
    if free is not None:
        scores['free'] = COEFFS['free'] * len(np.array(free).flatten()) / 2

    if defending is not None:
        scores['defend'] = COEFFS['defending'] * len(defending)

    gives_check = False
    if attacking is not None:
        attack = 0
        for sq in attacking:
            target = df.loc[sq, 'piece']
            if target == 'king':
                gives_check = True
                scores['check'] = COEFFS['check']
            else:
                scores['attack'] += (PIECE_BASE_VALUES[target]
                                     * COEFFS['attacking'])

    score = sum(scores.values())

    if df.loc[square, 'color'] == 'black':
        score =  - score

    # returns
    return free, attacking, defending, gives_check, score


def get_piece_domains(square, df):
    """
    Get the actual square domains affected by the piece.
    Return:
        attacking - list of (p_ square) tuples
        defending - list of (p_ square) tuples
        covering - list of squares
    """
    p_name = df.loc[square, 'piece']
    p_color = df.loc[square, 'color']
    # pawns move directionally - need to know color
    if p_name == 'pawn':
        p_name = p_color[0] + '_pawn'
    else:
        p_name = p_name

    raw_domains = RAW_DOMAINS[square][p_name]

    free = []
    attacking = []
    defending = []

    if p_name in ['rook', 'bishop', 'queen']:
        # these pieces have directional domains
        for direction in raw_domains:
            # work outwards
            for square in direction:
                # square is unoccupied
                if not square in df.index:
                    free.append(square)
                # square has friendly piece
                elif df.loc[square, 'color'] == p_color:
                    defending.append(square)
                    break # break because in a directional sequence
                # square has enemy piece
                else:
                    attacking.append(square)
                    break # break because in a directional sequence

    elif p_name in ['king', 'knight']:
        # these pieces have nondirectional domains
        for square in raw_domains:
            # square is unoccupied
            if not square in df.index:
                free.append(square)
            # square has friendly piece
            elif df.loc[square, 'color'] == p_color:
                defending.append(square)
                continue # not a directional sequence, just a set
            # square has enemy piece
            else:
                attacking.append(square)
                continue

    else: # pawn
        # raw domain for pawns has special structure, distinguishing squares
        # that are just covered (straight moves) vs attacked (diagonal taking)
        for square in raw_domains['covering']:
            if not square in df.index:
                free.append(square)
            else:
                continue

        for square in raw_domains['hitting']:
            if not square in df.index:
                continue
            elif df.loc[square, 'color'] == p_color:
                defending.append(square)
            else:
                attacking.append(square)

    return free, attacking, defending

