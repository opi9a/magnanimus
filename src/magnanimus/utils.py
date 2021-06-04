from termcolor import cprint

from .constants import PIECE_UNICODES, REV_PIECE_CODES


def test_print():
    print('\u2654')
    x = '\u2654'
    print(x)
    print(f"{x}")
    print(PIECE_UNICODES['white']['king'])

def print_board(board_arr=None, hlights=None):
    """
    Print the passed board array.
    Trad notation on west / south axes, np.array notation on north / east

    pass a list of squares to hlights and they will be identified with | |
    """

    print()
    black = False
    print("    ", end="")
    for col in range(8):
        print(f" {col} ", end=" ")
    print()

    row_names = range(1, 9)[::-1] # for trad notation
    for row in range(8):
        print(f" {row}  ", end="")
        for col in range(8):
            if board_arr is None:
                to_print = f"{row},{col}"
            elif board_arr[row, col] is None:
                to_print = (" ")
            else:
                color = board_arr[row, col].color
                p_name = board_arr[row, col].name
                to_print = (f"{PIECE_UNICODES[color][p_name]}")

            if hlights is not None and (row, col) in hlights:
                to_print = f"|{to_print}|"
            elif board_arr is not None:
                to_print = f" {to_print} "

            if black:
                cprint(to_print, on_color='on_white', attrs={'bold'}, end=" ")
                black = False
            else:
                cprint(to_print, attrs={'bold'}, end=" ")
                black = True

            if col == 7:
                black = not(black)
        print(f" {row_names[row]}  ")

    print('    ', end="")
    for col in 'abcdefgh':
        print(f" {col} ", end=" ")
    print()



def vec_from_trad(trad):
    """
    Return an np.array vector of coordinates for a passed trad notation
    position.

    >>> vec_from_trad('a7')
    1, 0
    """
    file, rank = trad
    row = 8 - int(rank)
    col = 'abcdefgh'.find(file)

    return row, col


def trad_from_vec(*vec):
    """
    Return trad notation version of passed np.array coordinates

    >>> trad_from_vec(1, 0)
    'a7'
    """
    row, col = vec
    rank = 8 - row
    file = 'abcdefgh'[col]

    return f"{file}{rank}"


def expand_color(color_init):
    if color_init.lower() == 'w':
        return 'white'
    elif color_init.lower() == 'b':
        return 'black'
    else:
        raise ValueError(f'cannot expand color {color_init}')

def expand_piece(piece_init):
    return REV_PIECE_CODES[piece_init.lower()]
