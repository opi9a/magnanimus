from datetime import datetime, timedelta
from .constants import INIT_BOARD_TUPLES, LOG, CASTLING_ROOK_MOVES
from .utils import invert_color
from .print_board import get_board_str
from .get_best_move import get_best_move
from .Position import Position, from_json
from .notation import trad_to_int

class Game():
    """
    Holds a position object with added metadata and methods 
    so it can run a game
    """
    
    def __init__(self, init_seed=None, color_playing='black',
                 pos_fp=None,
                 to_move='white', legal_castlings=None,
                 time_sec=5, auto_play=True, max_its=2):

        LOG.info('init magnanimo')

        # get the initial position
        if pos_fp is not None:
            self.position = from_json(pos_fp)
        else:
            self.position = Position(init_seed=init_seed,
                             to_move=to_move, legal_castlings=legal_castlings)

        # this will store past positions
        self.positions = []

        # operational parameters
        self.color_playing = color_playing
        self.time_sec = time_sec
        self.paths = []
        self.max_its = max_its

        # main loop
        if auto_play:
            self.auto_play(max_its)

    @property
    def score(self):
        return self.position.score

    @property
    def checked(self):
        return self.position.checked

    @property
    def df(self):
        return self.position.df

    def __repr__(self):
        """
        Overwrite the position repr for now
        """
        out = []
        pad = 20
        

        out.append(f'       black {-1 * self.score:.2f}')
        if self.position.to_move == 'black':
            out[-1] += '  to move'
        if self.checked == 'black':
            out[-1] += '  in check'
        out.append(get_board_str(self.df))
        out.append(f'       white {self.score:.2f}')
        if self.position.to_move == 'white':
            out[-1] += '  to move'
        if self.checked == 'white':
            out[-1] += '  in check'
        out.append('')


        return "\n".join(out)


    def next(self, max_its=None):
        """
        Do the next move
        """
        if self.position.moves:
            self.position.print_board(hlights=self.position.moves[-1])
        else:
            self.position.print_board()

        print(f'{self.checked} is checked')
        # get the opponent's move if its their go
        if self.color_playing != self.position.to_move:
            move = get_opponent_move(self.position)

        else:
            move, self.paths = get_best_move(self.position, return_positions=True,
                                             max_its=max_its)

        if move == 'x':
            return 'x'

        if move == 'checkmate':
            return 'checkmate'

        print(f'{self.position.to_move} move:', move)

        # update board and turn
        self.positions.append(self.position)
        self.position = Position(self.position, new_move=move)

        return 'ok'


    def auto_play(self, max_its):
        while True:
            status = self.next(max_its)
            if status == 'x':
                break
            if status == 'checkmate':
                break


    def undo_last(self):
        """
        Revert to previous position
        """
        self.position = self.positions[-1]


    # @property
    # def info(self):
    #     lengths_ser = self.paths_df['path'].apply(len).value_counts()
        
    #     return {
    #         'paths': len(self.paths_df),
    #         'lengths': [ (y,x) for x,y in lengths_ser.iteritems() ],
    #         'max path_len': lengths_ser.index.max(),
    #     }

def get_opponent_move(position):
    """
    TODO: accept trad
    """

    while True:
        raw_move = input(f'Your move as {position.to_move} - eg e2e4 (x to quit):  ')

        if raw_move:

            if raw_move in['x', 'q']:
                return 'x'

            if raw_move[0] == '0':
                zeros = raw_move.count('0')
                if position.to_move == 'black':
                    if zeros == 2:
                        move = CASTLING_ROOK_MOVES['black']['k']
                    elif zeros == 3:
                        move = CASTLING_ROOK_MOVES['black']['q']
                elif position.to_move == 'white':
                    if zeros == 2:
                        move = CASTLING_ROOK_MOVES['white']['k']
                    elif zeros == 3:
                        move = CASTLING_ROOK_MOVES['white']['q']

            else:
                move = trad_to_int(raw_move)

            if move in position.next_moves:
                return move

            position.print_board(hlights=move)

        print(f'{raw_move} is not legal try again')




