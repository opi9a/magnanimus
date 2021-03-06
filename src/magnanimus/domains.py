import operator
import pandas as pd

"""
CONSTANT

To use:
    from domains import RAW_DOMAINS
For each square:
    for each possible piece that may be there:
        squares covered by that piece (if empty board)
        may be directional (r, b, q, pawn initial move)
        ..or not (k, n, p other)

    will be used to get:
        covering squares (attack / defend)
        moving squares
    NB covering / moving are same for all pieces except pawns <shrugs>
"""

from .notation import vec_to_int_sq


def make_domains(int_squares=False):
    """
    Return a dict of squares, with the domains for each piece on that square

    For each square:
        for each possible piece:
            the squares that piece can reach (on an empty board)

    For bishop, rook, queen, and unmoved pawns the squares are arranged as
    ordered lists moving away from the root square (to enable handling of
    blocking pieces)

    For king, knight and moved pawns order is not reqd.  Use a single list
    (not list of lists)
    """
    out = {}

    for row in range(8):
        for col in range(8):
            out[row, col] = get_all_sq_domains(row, col, int_squares)
    
    if not int_squares:
        return out

    ints_out = {}

    for sq in out:
        a, b = sq
        ind = a*8 + b
        ints_out[ind] = out[sq]

    return ints_out


def get_all_sq_domains(row, col, int_squares):
    """
    Return a dict of all domains (by piece type) for the passed square
    """
    out = {}
    out['rook'] = make_axes(row, col, int_squares)
    out['bishop'] = make_diagonals(row, col, int_squares)
    out['knight'] = get_knight_domain(row, col, int_squares)
    out['queen'] = out['rook'] + out['bishop']
    out['king'] = [q_domain[0] for q_domain in out['queen']]
    out['w_pawn'] = get_pawn_domain('white', row, col, int_squares)
    out['b_pawn'] = get_pawn_domain('black', row, col, int_squares)

    return out


def make_diagonals(row, col, int_squares):
    """
    For each of 4 possible directions from the square, make a list
    of squares encountered
    """

    out = []

    for row_direction in [1, -1]:
        for col_direction in [1, -1]:

            direction_out = []
            new_row = row
            new_col = col

            while True:
                new_row += row_direction
                new_col += col_direction

                if legal_square(new_row, new_col):
                    direction_out.append((new_row, new_col))
                else:
                    break

            # only append if something there - avoid pointless empty tuples
            if direction_out:
                # making it a tuple (of tuples) helps with testing
                out.append(tuple(direction_out))

    if int_squares:
        ints_out = []
        for diag in out:
            ints_out.append([vec_to_int_sq(vec) for vec in diag])
        return ints_out

    return out


def make_axes(row, col, int_squares):
    """
    For each of 4 possible directions from the square, make a list
    of squares encountered
    """

    out = []

    for row_direction in [1, -1]:
        direction_out = []
        new_row = row
        while True:
            new_row += row_direction

            if legal_square(new_row, col):
                direction_out.append((new_row, col))
            else:
                break

        if direction_out:
            out.append(tuple(direction_out))

    for col_direction in [1, -1]:
        direction_out = []
        new_col = col
        while True:
            new_col += col_direction

            if legal_square(row, new_col):
                direction_out.append((row, new_col))
            else:
                break

        # making it a tuple (of tuples) helps with testing
        if direction_out:
            out.append(tuple(direction_out))

    if int_squares:
        ints_out = []
        for axis in out:
            ints_out.append([vec_to_int_sq(vec) for vec in axis])
        return ints_out

    return out


def get_knight_domain(row, col, int_squares):
    """
    Go 2 in each axis direction, then +1 -1 along other axis
    """

    out = []

    for row_incr in [2, -2]:
        for col_incr in [1, -1]:
            new_row = row + row_incr
            new_col = col + col_incr

            if legal_square(new_row, new_col):
                out.append((new_row, new_col))

    for col_incr in [2, -2]:
        for row_incr in [1, -1]:
            new_row = row + row_incr
            new_col = col + col_incr

            if legal_square(new_row, new_col):
                out.append((new_row, new_col))

    if int_squares:
        # its flat so no need to nest conversion
        return [vec_to_int_sq(vec) for vec in out]

    return out


def get_pawn_domain(color, row, col, int_squares):
    """
    Do on the fly because it is all so board-dependent?:
        ahead: squares the pawn can move to
        diagonal: squares the pawn can take on
    """
    if color[0] == 'w':
        op = operator.sub
        home_row = 6
    else:
        op = operator.add
        home_row = 1

    ahead = []
    main_move = (op(row, 1), col)
    if legal_square(*main_move):

        ahead.append(main_move)
        if row == home_row:
            ahead.append((op(row, 2), col))

    diagonal = [
        sq for sq in [(op(row, 1), col + 1), (op(row, 1), col - 1)]
        if legal_square(*sq)
    ]

    if int_squares:
        ahead = [vec_to_int_sq(sq) for sq in ahead]
        diagonal = [vec_to_int_sq(sq) for sq in diagonal]

    return {
        'ahead': ahead,
        'diagonal': diagonal,
    }


def legal_square(row, col):
    return (0 <= row < 8) and (0 <= col < 8)


def test_domains():

    diagonals = make_all_diagonals()

    target_diagonals_44 = {
        ( (3,3), (2,2), (1,1), (0,0) ),
        ( (5,5), (6,6), (7,7) ),
        ( (3,5), (2,6), (1,7) ),
        ( (5,3), (6,2), (7,1) ),
   }

    assert set(diagonals[(4,4)]) == target_diagonals_44

    target_diagonals_12 = {
        ( (2,3), (3,4), (4,5), (5,6), (6,7) ),
        ( (0,1), ),
        ( (0,3), ),
        ( (2,1), (3,0) ),
   }

    assert set(diagonals[(1,2)]) == target_diagonals_12

    print('ok')


RAW_DOMAINS = make_domains(int_squares=True)
