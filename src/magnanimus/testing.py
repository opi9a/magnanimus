
from .utils import make_board_from_tuples

TEST_TUPLES = [
    ('pawn', 'white', 6, 0),
    ('pawn', 'black', 5, 1),
    ('king', 'black', 0, 7),
    ('king', 'white', 7, 7),
    ('rook', 'white', 1, 0),
]

TEST_BOARD_ARR = make_board_from_tuples(TEST_TUPLES)
