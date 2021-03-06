from pathlib import Path
from my_tools.logging import get_filelog

DATA_DIR = Path('~/.magnanimus/data').expanduser()
LOG_DIR = Path('~/.magnanimus/logs').expanduser()
LOG = get_filelog(logfile_path=LOG_DIR / 'magnanimus.log')

PIECE_CODES = {
    'pawn': 'p',
    'rook': 'r',
    'knight': 'n',
    'bishop': 'b',
    'king': 'k',
    'queen': 'q',
}

REV_PIECE_CODES = { v: k for k, v in PIECE_CODES.items() }

INIT_BOARD_TUPLES = (
    [(REV_PIECE_CODES[pc], 'black', sq)
     for sq, pc in enumerate('rnbqkbnr')] + 

    [('pawn', 'black', sq + 8) for sq in range(8)] + 

    [('pawn', 'white', sq + 48) for sq in range(8)] + 

    [(REV_PIECE_CODES[pc], 'white', sq + 56)
     for sq, pc in enumerate('rnbqkbnr')]
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

CASTLING_ROOK_MOVES = {
    'black': {'k': (107, 5), 'q': (100, 3)},
    'white': {'k': (163, 61), 'q': (156, 59)},
}
