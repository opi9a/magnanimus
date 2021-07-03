import numpy as np

from .utils import invert_color
from .analyse import analyse_board

class Path():
    """
    Holds the board df and meta info
    """
    def __init__(self, prev_path=None, move=None,
                 df=None, moves=None, to_move=None):
        """
        Either init from scratch with df and moves, or update one passed
        attrs:
            df
            moves
            score
            is_check
            to_move
            next_moves
        """
        # if updating an existing path with a move
        if prev_path is not None:
            self.moves = prev_path.moves + [move]
            self.df = update_df(prev_path.df, move)
            self.to_move = invert_color(prev_path.to_move)

        # if init a new path
        else:
            self.moves = moves or []
            self.df = df
            self.to_move = to_move

        self.score = self.df['score'].sum()
        self.next_moves = get_df_next_moves(self.df, self.to_move)
        self.mate = False
        self.move = move

    def __repr__(self):
        pad = 15
        out = []
        if self.move is not None:
            out.append('\nMOVE: '.ljust(pad) + f'{self.move}'.rjust(pad))
        out.append('')
        df_strs = str(self.df).split('\n')
        out.extend(['sq' + df_strs[0][2:]] + df_strs[2:])

        out.append('')
        out.append('score:'.ljust(pad) + f'{self.score:.2f}'.rjust(pad))
        out.append('to_move:'.ljust(pad) + self.to_move.rjust(pad))
        out.append('checked:'.ljust(pad) + f'{self.checked}'.rjust(pad))
        out.append('mate:'.ljust(pad) + f'{self.mate}'.rjust(pad))

        moves_str = ", ".join(f"{sq_from}-{sq_to}"
                              for sq_from, sq_to in self.next_moves or [])
        out.append('next_moves:'.ljust(pad) + moves_str.rjust(pad))

        return "\n".join(out)

    @property
    def checked(self):
        """
        Return black, white or None
        """
        if is_checked(self.df) is not None:
            return is_checked(self.df)[0]
        else:
            return None


def is_checked(df):
    """
    Return list of colors or None
    May be both, in which case is illegal
    """
    if not any(df['gives_check']):
        return None
    
    checks = df.loc[df['gives_check'], 'color'].unique()

    # need to invert as the df has color GIVING check
    return [invert_color(check) for check in checks]


def update_df(df, move, analyse=True):
    """
    Pass a move
    Do the move
    Find pieces to change
    Change them
    Get their scores
    Return the df
    """
    df = df.copy()

    # if a piece is getting taken drop it first 
    if move[1] in df.index:
        df.drop(move[1], inplace=True)

    # move the piece simply by renaming the index
    df.rename(index={move[0]: move[1]}, inplace=True)

    squares_to_reanalyse = get_squares_to_reanalyse(df, move)

    if analyse:
        df = analyse_board(df, squares_to_reanalyse)

    return df

def get_squares_to_reanalyse(df, move):
    """
    get list of squares where either move[0] or move[1] is in
    available

    need to include pieces that were defending the moved square
    """
    all_sq = df[['free', 'attacking', 'defending']].sum(axis=1)
    squares_to_reanalyse = [
        square for square in df.index
        if set(all_sq[square]).intersection(move)
    ]

    return squares_to_reanalyse


def get_df_next_moves(df, to_move):
    """
    For all pieces with to_move color, return tuples for poss moves
    """

    out = []

    df = df.loc[df['color'] == to_move]

    for square in df.index:
        for next_square in df.loc[square, ['free', 'attacking']].sum():
            out.append((square, next_square))

    return out

