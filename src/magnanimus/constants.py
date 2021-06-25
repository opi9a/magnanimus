from pathlib import Path

from my_tools.logging import get_filelog

DATA_DIR = Path('~/.magnanimus/data').expanduser()
LOG_DIR = Path('~/.magnanimus/logs').expanduser()
LOG = get_filelog(logfile_path=LOG_DIR / 'magnanimus.log')

BASE_COLS = ['piece', 'color', 'row', 'col']

PATHS_DF_COLS = ['path', 'to_move', 'df', 'score', 'next_moves']

PIECE_CODES = {
    'pawn': 'p',
    'rook': 'r',
    'knight': 'n',
    'bishop': 'b',
    'king': 'k',
    'queen': 'q',
}

REV_PIECE_CODES = { v: k for k, v in PIECE_CODES.items() }

# you are here: make this ((row, col), 'color', 'piece')
INIT_BOARD_TUPLES = (
    [(REV_PIECE_CODES[pc], 'black', 0, col)
     for col, pc in enumerate('rnbqkbnr')] + 
    [('pawn', 'black', 1, col) for col in range(8)] + 
    [('pawn', 'white', 6, col) for col in range(8)] + 
    [(REV_PIECE_CODES[pc], 'white', 7, col)
     for col, pc in enumerate('rnbqkbnr')]
)

PIECE_UNICODES = {
    'white': {
       'king': '\u2654',
       'queen': '\u2655',
       'rook': '\u2656',
       'bishop': '\u2657',
       'knight': '\u2658',
       'pawn': '\u2659',
    },
    'black':{
       'king': '\u265A',
       'queen': '\u265B',
       'rook': '\u265C',
       'bishop': '\u265D',
       'knight': '\u265E',
       'pawn': '\u265F',
    }
}
