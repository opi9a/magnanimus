
from .utils import make_board_from_tuples

TEST_TUPLES = [
    ('queen', 'white', 1, 0),
    ('queen', 'black', 1, 6),
    ('king', 'black', 0, 7),
    ('king', 'white', 7, 7),
]

TEST_BOARD_ARR = make_board_from_tuples(TEST_TUPLES)

KINGS_ONLY = [
    ('king', 'black', 0, 7),
    ('king', 'white', 7, 7),
]
