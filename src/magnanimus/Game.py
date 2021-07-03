"""
Simple chess player

Board:
    minimal encoding of pieces + locations
    extract score and next moves (do this together) (color dependent)
    apply a move (or series) to get a new board

Move - pair of squares:
    [(0,4),(1,5)]

Path - sequence of game moves:
    [move1, move2, move3]

Path list:
    Fields: path (list of moves), score, next_moves

path    score   next_moves
----    -----   ----------
[]          0   [((1,1),(2,1))]

YOU ARE HERE you are here

1. in extend paths pick only the top N evaluated next moves to add back to paths_df
    - careful to sort by ascending or not depending on color relevant for that move

2. checkmate
3. record games
4. tweak scoring to make pieces more valuable
"""
import pandas as pd
import  numpy as np
from datetime import datetime, timedelta
from .constants import INIT_BOARD_TUPLES, LOG
from .utils import invert_color, make_board_df
from .print_board import print_board, get_board_str
from .get_best_move import get_best_move, Path
from .analyse import analyse_board, analyse_piece
from .Path import update_df, get_df_next_moves, is_checked
from .notation import trad_to_int


class Game():
    
    def __init__(self, piece_tuples=None, color_playing='black',
                 to_move='white', time_sec=5, auto_play=True):

        LOG.info('init magnanimo')
        self.color_playing = color_playing
        self.to_move = to_move
        self.last_move = None
        self.time_sec = time_sec

        # set attributes with initial status
        df = make_board_df(piece_tuples or INIT_BOARD_TUPLES)
        self.df = analyse_board(df)

        self.paths = [Path(df=self.df, to_move=self.to_move)]
        self.moves = []

        # main loop
        if auto_play:
            self.auto_play()

    @property
    def score(self):
        self.df = analyse_board(self.df)
        return self.df['score'].sum()

    @property
    def scores(self):
        score = self.score
        return {
            'white': score,
            'black': -score
        }

    @property
    def is_checked(self):
        # assume only the color to move can be actually in check
        if is_checked(self.df) is not None:
            return is_checked(self.df)[0]
        else:
            return None

    def __repr__(self):
        out = []
        pad = 20
        

        out.append(f'       black {-1 * self.score:.2f}')
        if self.to_move == 'black':
            out[-1] += '  to move'
        if self.is_checked == 'black':
            out[-1] += '  in check'
        out.append(get_board_str(self.df))
        out.append(f'       white {self.score:.2f}')
        if self.to_move == 'white':
            out[-1] += '  to move'
        if self.is_checked == 'white':
            out[-1] += '  in check'
        out.append('')


        return "\n".join(out)

    def __getitem__(self, sq):
        return self.df.loc[sq]

    def score_piece(self, sq):
        """
        For piece (trad or int) return the scoring
        """
        orig_sq = sq

        if isinstance(sq, str):
            sq = trad_to_int(sq)

        if not sq in self.df.index:
            print(f"no piece at {orig_sq}")

        free, attacking, defending, gives_check, score = (
            analyse_piece(sq, self.df))

        return {
            'color': self.df.loc[sq]['color'],
            'piece': self.df.loc[sq]['piece'],
            'free': free,
            'attacking': attacking,
            'defending': defending,
            'gives_check': gives_check,
            'score': score
        }

    def score_board(self, move=None):

        if move is not None:
            if isinstance(move, str):
                move = (trad_to_int(move[:2]),
                        trad_to_int(move[2:]))

            df = update_df(self.df, move)
        else:
            df = self.df
        return analyse_board(df)

    def make_moves(self, moves, auto_change_to_move=True):
        """
        Pass a string like "e2e4 d7d6 b1c3"
        """
        move_strs = moves.split()

        moves = []

        for move_str in move_strs:
            moves.append((trad_to_int(move_str[:2]),
                          trad_to_int(move_str[2:])))

        if auto_change_to_move:
            to_move = 'change'
        else:
            to_move = None

        for move in moves:
            self.moves.append(move)
            self.update_board(move, to_move=to_move)


    def update_board(self, move, to_move=None):
        """
        Update the board_df
        """
        if isinstance(move, str):
            move = (trad_to_int(move[:2]), trad_to_int(move[2:]))

        self.df = update_df(self.df, move)

        if to_move == 'change':
            self.to_move = invert_color(self.to_move)

        elif to_move is not None:
            self.to_move = to_move


    def undo_last(self, no_to_undo=1):
        """
        Undo last move
        """
        i = 0

        while i < no_to_undo:
            last_move = self.moves.pop()

            self.update_board(last_move[::-1])
            self.to_move = invert_color(self.to_move)
            print(f'undoing move {last_move} by {self.to_move}')
            i += 1


    def next(self):
        """
        Do the next move
        """
        print_board(self.df, hlights=self.last_move)

        if self.is_checked is not None:
            print(f'{self.is_checked} is checked')
        # get the opponent's move if its their go
        if self.color_playing != self.to_move:
            move = get_opponent_move(self.df, self.to_move)

        else:
            move = self.get_my_move()

        if move == 'x':
            return 'x'

        if move == 'checkmate':
            return 'checkmate'

        print(f'{self.to_move} move:', move)

        # update board and turn
        self.df = update_df(self.df, move)
        self.df = analyse_board(self.df)
        self.last_move = move
        self.to_move = invert_color(self.to_move)
        self.moves.append(move)

        return 'ok'

    def auto_play(self):
        while True:
            status = self.next()
            if status == 'x':
                break
            if status == 'checkmate':
                break


    def get_my_move(self):
        """
        With existing paths
        Current board
        Get possible moves (for me)
        Score them all
        """
        move, paths = get_best_move(self.df, self.color_playing,
                                    return_paths=True)

        self.paths = paths
        return move


    def print_board(self, next_moves_color=None):
        """
        Pass a color for next moves
        """
        if next_moves_color is not None:
            next_moves = get_df_next_moves(self.df, next_moves_color)
            destinations = [move[1] for move in next_moves]
        else:
            destinations = None

        print_board(self.df, scores=self.scores, hlights=destinations)

    @property
    def info(self):
        lengths = [len(p.next_moves) for p in self.paths]
        
        return {
            'paths': len(self.paths),
            'next_moves': np.product(lengths),
        }

    def init_paths(self):
        """
        For a given board df, init a paths list
        """
        self.paths = [
            {
                'path': [],
                'df': self.df,
                'score': self.score,
                'next_moves': self.next_moves,
            }

        ] 

def get_opponent_move(board_df, to_move):
    """
    TODO: accept trad
    """

    while True:
        move_str = input(f'Your move as {to_move} - eg e2e4 (x to quit):  ')

        if move_str == 'x':
            return 'x'
        
        move = [trad_to_int(x) for x in (move_str[:2], move_str[-2:])]

        legit_moves = get_df_next_moves(board_df, to_move)

        if tuple(move) in legit_moves:
            return move

        print(f'{move} is not legal try again')



