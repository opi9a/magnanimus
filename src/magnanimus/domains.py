import numpy as np
import operator

"""
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

def make_domains():
    """
    Return a board array of domains

    For each square:
        for each possible piece:
            the squares that piece can reach (on an empty board)

    For bishop, rook, queen, and unmoved pawns the squares are arranged as
    ordered lists moving away from the root square (to enable handling of
    blocking pieces)

    For king, knight and moved pawns the 
    """
    out = np.array([None]*64).reshape(8, 8)

    for row in range(8):
        for col in range(8):
            out[row, col] = get_all_sq_domains(row, col)
    return out


def get_all_sq_domains(row, col):
    """
    Return a dict of all domains (by piece type) for the passed square
    """
    out = {}
    out['rook'] = make_axes(row, col)
    out['bishop'] = make_diagonals(row, col)
    out['knight'] = get_knight_domain(row, col)
    out['queen'] = out['rook'] + out['bishop']
    out['king'] = [q_domain[0] for q_domain in out['queen']]
    out['w_pawn'] = get_pawn_domain('white', row, col)
    out['b_pawn'] = get_pawn_domain('black', row, col)

    return out


def make_diagonals(row, col):
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

    return out


def make_axes(row, col):
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

    return out


def get_knight_domain(row, col):
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

    return out


def get_pawn_domain(color, row, col):
    """
    Do on the fly because it is all so board-dependent?:
        covering: diag only
        moving: 1 or 2, all only if clear
    """
    if color[0] == 'w':
        op = operator.sub
        home_row = 6
    else:
        op = operator.add
        home_row = 1

    covering = []
    main_move = (op(row, 1), col)
    if legal_square(*main_move):

        covering.append(main_move)
        if row == home_row:
            covering.append((op(row, 2), col))

    hitting = [
        sq for sq in [(op(row, 1), col + 1), (op(row, 1), col - 1)]
        if legal_square(*sq)
    ]

    return {
        'covering': covering,
        'hitting': hitting,
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


