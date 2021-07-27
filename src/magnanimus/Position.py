
import numpy as np
import json
from copy import deepcopy

from .utils import invert_color, make_board_df
from .analyse import analyse_board
from .scoring import CASTLE_SCORE, CHECKMATE_SCORE
from .constants import INIT_BOARD_TUPLES, CASTLING_ROOK_MOVES
from .notation import trad_to_int, int_to_trad
from .print_board import print_board



class Position():
    """
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
                 init_seed=None, init_df=None,
                 prev_moves=None, to_move=None, legal_castlings=None):
        """
        Either init from scratch with df and moves, or update one passed
        prev_moves is for record, not currently for replaying or anything
        """

        self.just_castled = False
        # if updating an existing path with a move
        if prev_posn is not None:
            # work out if castling move and do some prep
            # NB don't need to check if legal, done in get_pos_next_moves

            if (prev_posn.legal_castlings[prev_posn.to_move]
                and new_move[0] >= 100):
                    # make the king move, adjust the castling state
                    df, self.legal_castlings = castling_prep(prev_posn,
                                                             new_move)
                    # adjust the move to be just the rook one
                    new_move = new_move[0] - 100, new_move[1]
                    self.just_castled = True
            else:
                df = prev_posn.df.copy()
                self.legal_castlings = prev_posn.legal_castlings

            self.df = update_df(df, new_move) # doesn't make another copy
            self.to_move = invert_color(prev_posn.to_move)

            if self.just_castled:
                self.moves = prev_posn.moves + [(new_move[0] + 100, new_move[1])]
            else:
                self.moves = prev_posn.moves + [new_move]

            self._score = 0
            

        # if init a new path
        else:
            self.moves = prev_moves or []
            # if theres an init_df use it, else tuples (new game by default)
            if init_df is not None:
                self.df = init_df
            else:
                if init_seed is None:
                    init_seed = INIT_BOARD_TUPLES
                self.df = make_board_df(init_seed)

            if to_move is None:
                print('Setting to_move as white')
                self.to_move = 'white'
            else:
                self.to_move = to_move

            self.df = analyse_board(self.df)

            if legal_castlings is not None:
                self.legal_castlings = {'white': [], 'black': []}
                for color, value in legal_castlings.items():
                    self.legal_castlings[color] = value
            else:
                self.legal_castlings = {
                    color: ['k', 'q']
                    for color in ['white', 'black']
                }

            
        # TODO this
        self.mated = None


    def __repr__(self):
        pad = 15
        out = []
        if self.moves:
            out.append('\nMOVES: '.ljust(pad) + f'{self.moves}'.rjust(pad))
        out.append('')
        df_strs = str(self.df).split('\n')
        out.extend(['sq' + df_strs[0][2:]] + df_strs[2:])

        out.append('')
        out.append('score:'.ljust(pad) + f'{self.score:.2f}'.rjust(pad))
        out.append('to_move:'.ljust(pad) + self.to_move.rjust(pad))
        out.append('checked:'.ljust(pad) + f'{self.checked}'.rjust(pad))
        out.append('mate:'.ljust(pad) + f'{self.mated}'.rjust(pad))

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
        """
        Remember black pieces are scored negatively already
        """
        score_from_df = self.df['score'].sum()

        if self.mated is not None:
            return CHECKMATE_SCORE * (-1 if self.mated == 'black' else 1)

        if self.just_castled:
            # if white is to move it means the scored move was by black
            castle_score = CASTLE_SCORE * (-1 if self.to_move == 'white' else 1)
            return castle_score + score_from_df
        else:
            return score_from_df


    @property
    def scores(self):
        score = self.score
        return {
            'white': score,
            'black': -score
        }

    @property
    def next_moves(self):
        return get_pos_next_moves(self)

    def print_board(self, next_moves_color=None, hlights=None):
        """
        Pass a color whose next moves will be shown
        """
        if next_moves_color is not None:
            next_moves = get_pos_next_moves(self, next_moves_color)
            destinations = [move[1] for move in next_moves]
        else:
            destinations = hlights

        print_board(self.df, to_move=self.to_move,
                    scores=self.scores, hlights=destinations)

    def to_json(self, fpath):
        """
        Save as json
        """

        out = {
            field: self.__dict__[field]
            for field in ['moves', 'to_move', 'legal_castlings']
        }
        out['piece_tuples'] = [
            (*self.df.loc[sq, ['piece', 'color']].values, sq)
            for sq in self.df.index
        ]

        with open(fpath, 'w') as fp:
            json.dump(out, fp, indent=4)


def from_json(fpath):
    with open(fpath, 'r') as fp:
        raw_json = json.load(fp)

    return Position(
        init_seed=raw_json['piece_tuples'],
        to_move=raw_json['to_move'],
        prev_moves=raw_json['moves'],
        legal_castlings=raw_json['legal_castlings']
    )



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
    all_sq = df[['free', 'attacking',
                 'just_covering', 'defending']].sum(axis=1)
    squares_to_reanalyse = [
        square for square in df.index
        if set(all_sq[square]).intersection(move)
    ]

    return squares_to_reanalyse


def get_pos_next_moves(pos, next_moves_color=None):
    """
    For all pieces with to_move color, return tuples for poss moves
    """

    out = []
    
    next_moves_color = next_moves_color or pos.to_move

    df = pos.df.loc[pos.df['color'] == next_moves_color]

    for square in df.index:
        for next_square in df.loc[square, ['free', 'attacking']].sum():
            out.append((square, next_square))
            
    if pos.legal_castlings[next_moves_color]:
        castlings = get_castlings(pos)
        if castlings:
            out.extend(castlings)

    return out


def castling_prep(position, move):
    """
    Pre-process the df when the move is castling, by moving the king
    (so that move / board analysis can proceed as normal using the rook
     component of the castling move)

    Also return updated castling state
    """

    df = position.df.copy()
    legal_castlings = deepcopy(position.legal_castlings)

    # find out if black or white, k or q
    if move[0] == 100:
        df.rename(index={4: 2}, inplace=True)
        legal_castlings['black'].remove('q')
    elif move[0] == 107:
        df.rename(index={4: 6}, inplace=True)
        legal_castlings['black'].remove('k')
    elif move[0] == 156:
        df.rename(index={60: 58}, inplace=True)
        legal_castlings['white'].remove('q')
    elif move[0] == 163:
        df.rename(index={60: 62}, inplace=True)
        legal_castlings['white'].remove('k')

    return df, legal_castlings


def get_castlings(position):
    """
    to get this far means there must be some legal_castlings, 
    i.e. king and relevant rook has not moved, so don't need to check that
    """
    df = position.df
    legal_castlings = position.legal_castlings[position.to_move]
    out = []

    if 'k' in legal_castlings:
        if position.to_move == 'white':
            # check space between is free
            if not len(df.index.intersection([61, 62])):
                out.append(CASTLING_ROOK_MOVES['white']['k'])
        else:
            # check space between is free
            if not len(df.index.intersection([5, 6])):
                out.append(CASTLING_ROOK_MOVES['black']['k'])


    if 'q' in legal_castlings:
        if position.to_move == 'white':
            # check space between is free
            if not len(df.index.intersection([57, 58, 59])):
                out.append(CASTLING_ROOK_MOVES['white']['q'])
        else:
            # check space between is free
            if not len(df.index.intersection([1, 2, 3])):
                out.append(CASTLING_ROOK_MOVES['black']['q'])

    return out

