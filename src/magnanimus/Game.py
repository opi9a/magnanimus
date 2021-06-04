import numpy as np
import pandas as pd

"""
Game:
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
from .constants import INIT_BOARD_TUPLES, REV_PIECE_CODES
from .utils import (trad_from_vec, vec_from_trad, print_board,
                    expand_color, expand_piece)
from .Piece import Piece
from .domains import make_domains

# get the empty-board domains (by square, by piece)
RAW_DOMAINS = make_domains()

BASE_COLS = ['piece', 'color', 'row', 'col']


class Game():

    def __init__(self, file_path=None, piece_tuples=None):
        """
        Make a board - usually to start a game - and calculate metadata
        """
        if file_path is None and piece_tuples is None:
            piece_tuples = INIT_BOARD_TUPLES

        # private attrs have public property versions
        self._board = make_board(file_path=file_path,
                                 piece_tuples=piece_tuples)

        self._pieces_df = None
        self._scores = None
        self._net_score = None

        self.calculate() # sets the data above

    # METHODS
    def calculate(self):
        """
        Recalculate domains and scores for each piece
        Generate overall scores (currently using the self.pieces_df)
        """

        piece_data = []
        for row in range(8):
            for col in range(8):

                piece = self._board[row, col]

                if piece is None:
                    continue

                piece.calculate(self._board)
                piece_data.append([piece.name, piece.color,
                                   *piece.square, piece.score])

        df = pd.DataFrame(piece_data, columns=BASE_COLS + ['score'])
        df = df.sort_values(['color'], ascending=False)
        self._pieces_df = df

        self._scores = df.groupby('color')['score'].sum()
        self._net_score = self.scores['white'] - self.scores['black']

    def move(self, sq_from, sq_to):
        """
        Check move is legal
        Set sq_to on board to the piece
        Change the square attr of the piece
        Set square left to None
        (delete taken piece if reqd ?)
        Recalculate everything
        TODO: handle check etc, eg when evaluating move legality
        """

        piece = self._board[sq_from]
        if not sq_to in piece.available:
            print(f'Cannot move {piece.name} at {sq_from} to {sq_to}')
            return
        self._board[sq_to] = self._board[sq_from]
        self._board[sq_to].square = sq_to # also set piece's square
        self._board[sq_from] = None

        self.calculate()

    def tmove(self, from_to_str, show_after=True):
        """
        Make a move using trad notation eg:
        >>> game.tmove('e2e4')

        TODO: accept proper trad eg 'e4'
        """
        t_from = from_to_str[:2]
        t_to = from_to_str[2:]
        self.move(vec_from_trad(t_from), vec_from_trad(t_to))

        self.show()


    # PROPERTIES
    @property
    def board(self):
        return self._board

    @property
    def pieces_df(self):
        """
        Public property for the pieces df
        """
        df = self._pieces_df.copy()

        df['trad_square'] = df.apply(
            lambda x: trad_from_vec(x['row'], x['col']),
            axis=1
        )

        return df

    @property
    def scores(self):
        return {color: self._scores[color] for color in ['white', 'black']}

    @property
    def net_score(self):
        return round(self._net_score, 2)

    # CLASS STUFF
    def __getitem__(self, square):
        """
        Take a square tuple (np format) or string (trad format eg "e8")
        and return the piece there
        """
        if isinstance(square[0], int):
            # it is trad format so convert to np
            row, col = square
        else:
            row, col = vec_from_trad(square)

        if (0 <= row < 8) and (0 <= row < 8):
            return self._board[row, col]

        raise ValueError(f'square {square} is off the board')

    def __repr__(self):
        return str(self.pieces_df)

    # I/O
    def show(self):
        print_board(self._board)
        print(f'\n   W: {self.scores["white"]:.2f}, '
              f'B {self.scores["black"]:.2f} ',
              f'Net: {self.net_score:.2f}')

    def to_csv(self, filepath):
        self.pieces_df.to_csv(filepath, index=False)



def make_board(file_path=None, piece_tuples=None):
    """
    Return an np array representing the board
    """

    # prepare inputs
    if file_path is not None:
        df = pd.read_csv(file_path)
        
        if 'trad_square' in df.columns and not(
            'row' in df.columns and 'col' in df.columns
        ):
            df['row'], df['col'] = zip(*df['trad_square'].apply(vec_from_trad))

    else:
        if piece_tuples is None:
            piece_tuples = INIT_BOARD_TUPLES

        df = pd.DataFrame(piece_tuples, columns=BASE_COLS)

    if df['color'].apply(len).max() == 1:
        df['color'] = df['color'].apply(expand_color)

    if df['piece'].apply(len).max() == 1:
        df['piece'] = df['piece'].apply(expand_piece)

    # an empty board
    board_arr = np.array([None]*64).reshape(8, 8)

    # place the pieces
    for i in df.index:
        board_arr[df.loc[i]['row'], df.loc[i]['col']] = Piece(
            name = df.loc[i]['piece'],
            color = df.loc[i]['color'],
            row = df.loc[i]['row'],
            col = df.loc[i]['col'],
            board=None,
        )

    # now pieces in place calculate their domains and scores
    for row in range(8):
        for col in range(8):
            if board_arr[row, col] is not None:
                board_arr[row, col].calculate(board_arr)

    return board_arr



