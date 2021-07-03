from termcolor import cprint

from .constants import PIECE_UNICODES
from .utils import make_board_df
from .notation import vec_to_int_sq


def print_board(board_df=None, scores=None, hlights=None, use_ints=True):
    """
    Print the passed board array.
    Trad notation on west / south axes, np.array notation on north / east

    pass a list of squares to hlights and they will be identified with | |
    """

    df = board_df

    print()
    
    if scores is not None: print('    Black:', f"{scores['black']:.3f}")

    black = False
    print("     ", end="")
    for col in range(8):
        print(f" {col} ", end=" ")
    print()

    row_names = range(1, 9)[::-1] # for trad notation
    for row in range(8):
        print(f" {row * 8:>2}  ", end="")
        for col in range(8):
            int_sq = vec_to_int_sq(row, col)
            if df is None:
                piece = None
                if use_ints:
                    to_print = f"{int_sq:>3}"
                else:
                    to_print = f"{row},{col}"
            else:
                piece = df.T.get(int_sq)

                if piece is None:
                    to_print = (" ")
                else:
                    color, p_name = piece['color'], piece['piece']
                    to_print = (f"{PIECE_UNICODES[color][p_name]}")

            if hlights is not None and int_sq in hlights:
                to_print = f"|{to_print}|"
            elif df is not None:
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

    print('     ', end="")
    for col in 'abcdefgh':
        print(f" {col} ", end=" ")
    print()
    if scores is not None: print('    White:', f"{scores['white']:.3f}")


def get_board_str(board_df=None, board_tuples=None, 
                scores=None, hlights=None):
    """
    Return a board_arr string representation
    """

    if board_df is None:
        board_df = make_board_df(board_tuples)

    out = []
    
    if scores is not None:
        out.append('    Black:', f"{scores['black']:.3f}")

    black = False

    col_line = ["     "]
    for col in range(8):
        col_line.append(f" {col} ")
    out.append("".join(col_line))

    row_names = range(1, 9)[::-1] # for trad notation
    for row in range(8):
        row_line = [f" {row * 8:>2}  "]
        for col in range(8):

            int_sq = vec_to_int_sq(row, col)

            if board_df is None:
                to_print = f"{int_sq:>2}"
            elif int_sq not in board_df.index:
                to_print = ("\u00B7")
            else:
                color, p_name = board_df.loc[int_sq, ['color', 'piece']]
                to_print = (f"{PIECE_UNICODES[color][p_name]}")

            if hlights is not None and int_sq in hlights:
                row_line.append(f"|{to_print}|")
            elif board_df is not None:
                row_line.append(f" {to_print} ")

        row_line.append(f" {row_names[row]}")
        out.append("".join(row_line))

    col_line = ["     "]
    for col in 'abcdefgh':
        col_line.append(f" {col} ")
    out.append("".join(col_line))


    return "\n".join(out)


