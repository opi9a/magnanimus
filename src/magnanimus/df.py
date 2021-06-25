import pandas as pd

from .domains import make_domains
from .scoring import score_piece

RAW_DOMAINS = make_domains()


def make_board_df(piece_tuples):
    """
    Make a new style df
    """
    df = pd.DataFrame(piece_tuples)
    df.columns = ['piece', 'color', 'row', 'col']
    df = df.set_index(['row', 'col'])
    df = add_domains(df)

    return df


def add_domains(df):
    """
    For a df with just pieces and colors, add available, attacking and
    defending lists of squares
    """

    df = df.copy()

    available = []
    attacking = []
    defending = []

    for square in df.index:
        a, b, c = get_actual_domains(square, df)
        available.append(a or None)
        attacking.append(b or None)
        defending.append(c or None)

    df['available'] = available
    df['attacking'] = attacking
    df['defending'] = defending

    df[['score', 'gives_check']] = df.apply(
        lambda x: score_piece(x, df), axis=1).apply(pd.Series)

    return df

def get_actual_domains(p_square, df):
    """
    Return:
        attacking - list of (p_ square) tuples
        defending - list of (p_ square) tuples
        covering - list of squares
    """
    p_name, p_color = df.loc[p_square].values
    # pawns move directionally - need to know color
    if p_name == 'pawn':
        p_name = p_color[0] + '_pawn'
    else:
        p_name = p_name

    raw_domains = RAW_DOMAINS[p_square][p_name]

    available = []
    attacking = []
    defending = []

    if p_name in ['rook', 'bishop', 'queen']:
        # these pieces have directional domains
        for direction in raw_domains:
            # work outwards
            for square in direction:
                # square is unoccupied
                if not square in df.index:
                    available.append(square)
                # square has friendly piece
                elif df.loc[square, 'color'] == p_color:
                    defending.append(square)
                    break
                # square has enemy piece
                else:
                    attacking.append(square)
                    break

    elif p_name in ['king', 'knight']:
        # these pieces have nondirectional domains
        for square in raw_domains:
            # square is unoccupied
            if not square in df.index:
                available.append(square)
            # square has friendly piece
            elif df.loc[square, 'color'] == p_color:
                defending.append(square)
                break
            # square has enemy piece
            else:
                attacking.append(square)
                break

    else: # pawn
        # raw domain for pawns has special structure, distinguishing squares
        # that are just covered (straight moves) vs attacked (diagonal taking)
        for square in raw_domains['covering']:
            if not square in df.index:
                available.append(square)
            else:
                break

        for square in raw_domains['hitting']:
            if not square in df.index:
                continue
            elif df.loc[square, 'color'] == p_color:
                defending.append(square)
            else:
                attacking.append(square)


    return available, attacking, defending


