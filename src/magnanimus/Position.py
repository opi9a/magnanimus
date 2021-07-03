
import numpy as np

from .utils import invert_color, make_board_df
from .analyse import analyse_board
from .constants import INIT_BOARD_TUPLES
# from .notation import trad

class Position():
    """
    YOU ARE HERE dev of this to replace Path, and much of Game

    Holds board and associated info and methods
    Intended for use both in Game (current state of the game) 
    and in projected positions

    Allow history to be accessed
    Does all the Game stuff like update board etc

    methods:
        update?  or just do this with init
        explore moves and scores for debug
        explain last move?
    """
    def __init__(self, prev_posn=None, new_move=None,
                 init_tuples=None, init_df=None,
                 prev_moves=None, to_move=None):
        """
        Either init from scratch with df and moves, or update one passed
        prev_moves is for record, not currently for replaying or anything
        """
        # if updating an existing path with a move
        if prev_posn is not None:
            self.df = update_df(prev_posn.df, new_move)
            self.to_move = invert_color(prev_posn.to_move)
            self.moves = prev_posn.moves + [new_move]

        # if init a new path
        else:
            self.moves = prev_moves or []
            # if theres an init_df use it, else tuples (new game by default)
            if init_df is not None:
                self.df = init_df
            else:
                if init_tuples is None:
                    init_tuples = INIT_BOARD_TUPLES
                self.df = make_board_df(init_tuples)

            if to_move is None:
                print('Setting to_move as white')
                self.to_move = 'white'
            else:
                self.to_move = to_move

            self.df = analyse_board(self.df)

        # TODO this
        self.mate = False

    def make_move(self, move):

        if isinstance(move, str):
            move = int
        self.df = update_df(self.df, move, analyse=True)
        self.moves.append(move)
        self.to_move = invert_color(self.to_move)


    def __repr__(self):
        pad = 15
        out = []
        # if self.move is not None:
        #     out.append('\nMOVE: '.ljust(pad) + f'{self.move}'.rjust(pad))
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

    @property
    def score(self):
        return self.df['score'].sum()

    @property
    def scores(self):
        score = self.score
        return {
            'white': score,
            'black': -score
        }

    @property
    def next_moves(self):
        return get_df_next_moves(self.df, self.to_move)


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

