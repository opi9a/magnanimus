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

you are here:
    dealing with check:
        DONE BUT NOT WORKING: have threatened_domain available to determine
        BUT doesn't seem to make it thru to thie kking (in piece)
        make illegal move (do this in Piece - if king)
        reflect in score (do this in Piece - if king)
        checkmate = 99 points (do this in Piece - if king)

"""
import pandas as pd
import  numpy as np
from datetime import datetime, timedelta
from .constants import INIT_BOARD_TUPLES, PIECE_CODES, LOG
from .analyse_board import analyse_board
from .utils import make_board_from_tuples, print_board
from .Piece import Piece

class Magnanimus():
    
    def __init__(self, piece_tuples=None, color_playing='black',
                 to_move='white', time_sec=5, _hl_threat=False):

        LOG.info('init magnanimo')
        self.board_arr = make_board_from_tuples(piece_tuples
                                                or INIT_BOARD_TUPLES)
        self.color_playing = color_playing
        self.to_move = to_move
        self.last_move = None
        # this holds the available moves after last move
        self.threatened_domain = None
        self._hl_threat = _hl_threat

        self.paths_df = None
        self.time_sec = time_sec

        # todo make analyse_board a class method - it always evals self variables
        # init scores etc - and threatened_domain which will be non player
        self.scores, self.net_score, self.threatened_domain = (
            analyse_board(self.board_arr, invert_color(self.to_move)))

        # main loop
        while True:
            # dev
            if self._hl_threat and self.threatened_domain is not None:
                hlights = [x[1] for x in self.threatened_domain]
            else:
                hlights = self.last_move
            print_board(self.board_arr, scores=self.scores,
                        to_move=self.to_move, hlights=hlights)
            # get the opponent's move if its their go
            if self.color_playing != self.to_move:
                move = get_opponent_move(self.board_arr, self.threatened_domain)

            else:
                move = self.get_my_move()

            if isinstance(move, str) and move == 'x':
                break

            print(f'{self.to_move} move:', move)

            # update board and turn
            self.board_arr = update_board(self.board_arr, [move])
            self.last_move = move
            self.to_move = invert_color(self.to_move)

            # get the scores and the checked domain
            # - this is the poss next moves of LAST player
            last_player = invert_color(self.to_move)
            self.scores, self.net_score, self.threatened_domain = (
                analyse_board(self.board_arr, last_player,
                    threatened_domain=self.threatened_domain)
            )

            print('threatened_domain', self.threatened_domain)


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
        init_scores, init_score, init_next_moves = analyse_board(
            self.board_arr, to_move=to_move, threatened_domain=self.threatened_domain)

        self.paths_df = get_empty_paths_df(init_score, init_next_moves)

        # loop extending paths
        max_it = 20
        its = 0
        timeout = datetime.now() + timedelta(seconds=self.time_sec)
        while True:
            self.paths_df = extend_paths(
                self.board_arr, self.paths_df, to_move,
                timeout=timeout)
            to_move = invert_color(to_move)
            its += 1
            if its == max_it or datetime.now() >= timeout:
                break

        # get best
        is_black = self.color_playing == 'black'
        self.paths_df = self.paths_df.sort_values('score', ascending=is_black)
        # to do:  rationalize paths df, dropping as reqd
        return tuple(self.paths_df.iloc[0]['path'][0])

    def print_board(self, hlights=None):
        print_board(self.board_arr, scores=self.scores)

    @property
    def info(self):
        lengths_ser = self.paths_df['path'].apply(len).value_counts()
        
        return {
            'paths': len(self.paths_df),
            'lengths': [ (y,x) for x,y in lengths_ser.iteritems() ],
            'max path_len': lengths_ser.index.max(),
        }

def get_empty_paths_df(init_score=None, init_next_moves=None):
    return pd.DataFrame([{
        'path': [],
        'score': init_score,
        'next_moves': init_next_moves, # a list of moves
    }])


def extend_paths(board_arr, paths_df, to_move, timeout=None):
    """
    Take a paths_df and return an extended version.

    path            score   next_moves
    ====            =====   ==========
    [((0,0),(5,5))]   3.4   [((5,5),(7,5)), ((5,5),(6,5))..]
    [((0,0),(5,4))]   3.8   [((5,4),(7,4)), ((5,4),(6,4))..]

    (return df with same structure but (more and) longer paths, new scores
     and new next_moves)

    path                           score   next_moves
    ====                           =====   ==========
    [((0,0),(5,5)), ((5,5),(7,5))]   7.5   [((7,5),(0,5))..]
    [((0,0),(5,5)), ((5,5),(6,5))]   2.4   [((6,5),(0,5))..]
    ...
    [((0,0),(5,4)), ((5,4),(7,4))]   3.1   [((7,4),(0,4))..]

    Create a new df with the extended paths.
    If timeout, append the old (un-extended) to it

    paths_out = []
    For each path:
        for each next move:
            make a board
            get score
            get next_moves
            add to paths_out
    make a new paths_df from paths_out
    append any unprocessed
    """


    paths_out = []
    # iterate over each existing path
    # NB each will spawn more paths, made from its next_moves
    for i, path, score, next_moves in paths_df.itertuples():
        LOG.info(f'iteration {i}')

        # make a board_arr for the passed path (cd be multiple moves)
        board_from_path = update_board(board_arr, path)

        for move in next_moves:
            # make a board_arr to simulate the move and record its data
            board_from_move = update_board(board_from_path, [move])
            scores, score, next_moves = analyse_board(board_from_move, to_move)
            
            paths_out.append([path + list([move]), score, next_moves])

        if datetime.now() >= timeout:
            LOG.info('stopping as past time')
            break

    df = pd.DataFrame(paths_out, columns=paths_df.columns)

    if i + 1 < len(paths_df):
        df = df.append(paths_df.iloc[i+1:])

    return df


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

def get_opponent_move(board_arr, threatened_domain):
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
            piece = Piece(board_arr, *sq_from, threatened_domain)
            if sq_to in piece.next_moves:
                return move

        print(f'{move} is not legal try again')

def invert_color(color):
    if color == 'black':
        return 'white'
    return 'black'
