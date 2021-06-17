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

"""
import pandas as pd
import  numpy as np
from datetime import datetime, timedelta
from .constants import INIT_BOARD_TUPLES, PIECE_CODES, LOG
from .analyse_board import analyse_board, elaborate_board
from .utils import (make_board_from_tuples, print_board, invert_color,
                    get_board_str, update_board)
from .Piece import Piece
from .extend_paths import extend_paths

class Magnanimus():
    
    def __init__(self, piece_tuples=None, color_playing='black',
                 to_move='white', time_sec=5, auto_play=True):

        LOG.info('init magnanimo')
        self.board_arr = make_board_from_tuples(piece_tuples
                                                or INIT_BOARD_TUPLES)
        self.color_playing = color_playing
        self.to_move = to_move
        self.last_move = None
        self.time_sec = time_sec

        scores, net_score, next_moves, is_checked = (
            analyse_board(self.board_arr, self.to_move))


        self.paths_df = get_empty_paths_df(to_move, init_score=net_score,
                                           init_next_moves=next_moves)

        self.scores = scores
        self.net_score = net_score
        self.next_moves = next_moves
        self.is_checked = is_checked


        # main loop
        if auto_play:
            while True:
                status = self.next()
                if status == 'x':
                    break

    def __repr__(self):
        out = []
        pad = 20
        
        out.append(f'       black: {self.scores["black"]:.2f}')
        if self.to_move == 'black':
            out[-1] += '  to move'
        out.append(get_board_str(self.board_arr))
        out.append(f'       white: {self.scores["white"]:.2f}')
        if self.to_move == 'white':
            out[-1] += '  to move'
        out.append('')


        return "\n".join(out)

    def __getitem__(self, sq):
        row, col = sq
        return Piece(self.board_arr, row, col)


    def next(self):
        """
        Do the next move
        """
        print_board(self.board_arr, scores=self.scores,
                    hlights=self.last_move)
        print(f'{self.is_checked} is checked')
        # get the opponent's move if its their go
        if self.color_playing != self.to_move:
            move = get_opponent_move(self.board_arr)

        else:
            move = self.get_my_move()

        if move == 'x':
            return 'x'

        print(f'{self.to_move} move:', move)

        # update board and turn
        self.board_arr = update_board(self.board_arr, [move])
        self.last_move = move
        self.to_move = invert_color(self.to_move)
        self.scores, self.net_score, self.next_moves, self.in_check = (
            analyse_board(self.board_arr, self.to_move))


    def get_my_move(self):
        """
        With existing paths
        Current board
        Get possible moves (for me)
        Score them all
        """
        # check time and exit

        to_move = self.color_playing

        # init paths_df with current board
        init_scores, init_score, init_next_moves, is_checked = analyse_board(
            self.board_arr, to_move=to_move)

        self.paths_df = get_empty_paths_df(init_score=init_score,
                           init_next_moves=init_next_moves, to_move=to_move)

        # loop extending paths
        max_it = 20
        its = 0
        timeout = datetime.now() + timedelta(seconds=self.time_sec)
        while True:
            self.paths_df = extend_paths(
                self.board_arr, self.paths_df, timeout=timeout)
            to_move = invert_color(to_move)
            its += 1
            if its == max_it or datetime.now() >= timeout:
                break

        # get best
        is_black = self.color_playing == 'black'
        self.paths_df = self.paths_df.sort_values('score', ascending=is_black)
        # to do:  rationalize paths df, dropping as reqd
        return tuple(self.paths_df.iloc[0]['path'][0])

    def print_board(self):
        print_board(self.board_arr, scores=self.scores)

    @property
    def info(self):
        lengths_ser = self.paths_df['path'].apply(len).value_counts()
        
        return {
            'paths': len(self.paths_df),
            'lengths': [ (y,x) for x,y in lengths_ser.iteritems() ],
            'max path_len': lengths_ser.index.max(),
        }

def get_empty_paths_df(to_move, init_score=None, init_next_moves=None):
    return pd.DataFrame([{
        'path': [],
        'score': init_score,
        'to_move': to_move,
        'next_moves': init_next_moves, # a list of moves
    }])



def get_opponent_move(board_arr):
    """
    TODO: accept trad
    """

    while True:
        raw_move = input('Your move rc,rc - eg 64,44 (x to quit):  ')

        if raw_move == 'x':
            return 'x'
        
        r0, c0, _, r1, c1 = raw_move
        move = ((int(r0), int(c0)), (int(r1), int(c1)))

        # get the piece being moved, to check move is legit
        sq_from, sq_to = move
        if board_arr[sq_from] is not None:
            piece = Piece(board_arr, *sq_from)
            if sq_to in piece.next_moves:
                return move

        print(f'{move} is not legal try again')
