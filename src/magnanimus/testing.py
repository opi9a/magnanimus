
from .utils import make_board_df

TEST_TUPLES = [
    ('queen', 'white', 1, 0),
    ('queen', 'black', 1, 6),
    ('rook', 'black', 2, 6),
    ('king', 'black', 0, 7),
    ('king', 'white', 7, 7),
]

TEST_BOARD_ARR = make_board_df(TEST_TUPLES)

SIMPLES = [
    ('knight', 'black', 0),
    ('king', 'white', 16),
]
KINGS_ONLY = [
    ('king', 'black', 0, 7),
    ('king', 'white', 7, 7),
]
IN_CHECK = [
    ('king', 'black', 0, 7),
    ('king', 'white', 7, 7),
    ('rook', 'white', 0, 0),
]
CHECK_IMMINENT = [
    ('king', 'black', 0, 7),
    ('king', 'white', 2, 7),
    ('rook', 'white', 1, 1),
]
CHECKMATE_IMMINENT = [
    ('king', 'black', 7),
    ('rook', 'white', 8),
    ('rook', 'white', 9),
    ('pawn', 'white', 16),
    ('pawn', 'white', 17),
]
