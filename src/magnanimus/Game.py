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
from .constants import INIT_BOARD_TUPLES, PIECE_CODES, LOG
from .utils import invert_color, make_board_df, vec_to_int_sq
from .print_board import print_board, get_board_str
from .get_best_move import get_best_move
from .Path import get_df_next_moves, Path
from .analyse import analyse_board

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

        # main loop
        if auto_play:
            self.auto_play()

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

    @property
    def paths(self):
        """
        What it will init with (not extended)
        """
        return Path(df=self.df, to_move=self.to_move)

    @property
    def is_checked(self):
        # assume only the color to move can be actually in check
        return any(self.df['gives_check'])

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


    def next(self):
        """
        Do the next move
        """
        print_board(self.df, hlights=self.last_move)
        print(f'{self.is_checked} is checked')
        # get the opponent's move if its their go
        if self.color_playing != self.to_move:
            move = get_opponent_move(self.df)

        else:
            move = self.get_my_move()

        if move == 'x':
            return 'x'

        if move == 'checkmate':
            return 'checkmate'

        print(f'{self.to_move} move:', move)

        # update board and turn
        self.board_arr = update_board(self.board_arr, [move])
        self.last_move = move
        self.to_move = invert_color(self.to_move)
        self.scores, self.net_score, self.next_moves, self.is_checked = (
            analyse_board(self.board_arr, self.to_move))

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
        # check time and exit

        to_move = self.color_playing

        # init paths with current board
        self.init_paths()

        # loop extending paths
        max_it = 2
        its = 0
        timeout = datetime.now() + timedelta(seconds=self.time_sec)
        while True:
            LOG.info(f'on it {its} of {max_it}, time {datetime.now()} of {timeout}')
            new_paths = extend_paths(self.paths)
            if new_paths is None:
                # checkmate
                return 'checkmate'
            else:
                self.paths = new_paths

            to_move = invert_color(to_move)
            its += 1
            if its == max_it or datetime.now() >= timeout:
                break

        # get best
        is_black = self.color_playing == 'black'
        self.paths_df = self.paths_df.sort_values('score', ascending=is_black)
        # to do:  rationalize paths df, dropping as reqd
        return tuple(self.paths_df.iloc[0]['path'][0])

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
        lengths_ser = self.paths_df['path'].apply(len).value_counts()
        
        return {
            'paths': len(self.paths_df),
            'lengths': [ (y,x) for x,y in lengths_ser.iteritems() ],
            'max path_len': lengths_ser.index.max(),
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
        raw_move = input(f'Your move as {to_move} - eg 64,44 (x to quit):  ')

        if raw_move == 'x':
            return 'x'
        
        r0, c0 = raw_move[:2]
        r1, c1 = raw_move[-2:]
        move = ((int(r0), int(c0)), (int(r1), int(c1)))
        move = (vec_to_int_sq(move[0]), vec_to_int_sq(move[1]))

        legit_moves = get_df_next_moves(board_df, to_move)

        if move in legit_moves:
            return move

        print(f'{move} is not legal try again')


