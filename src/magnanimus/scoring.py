import numpy as np

PIECE_BASE_VALUES = {
    'pawn': 1,
    'bishop': 3,
    'knight': 3,
    'rook': 5,
    'queen': 9,
    'king': 0,
}

COEFFS = {
    'avail': 0.2,
    'defending': 0.5,
    'attacking': 0.2, # NB this multiplies the points value of attacked piece
}


def score_piece(piece):
    """
    Return a value
    """
    base = PIECE_BASE_VALUES[piece.name]

    # you are here
    # work out scores as function of 

    # available may be a nested list, so flatten (row, col for each)
    avail = COEFFS['avail'] * len(np.array(piece.available).flatten()) / 2

    defend = COEFFS['defending'] * len(piece.defending)

    attack = sum(PIECE_BASE_VALUES[x[0]]
                 for x in piece.attacking) * COEFFS['attacking']

    # print('score for'.ljust(8), piece.color, piece.name)
    # print('base'.ljust(8), f'{base:>4.1f}')
    # print('avail'.ljust(8), f'{avail:>4.1f}')
    # print('defend'.ljust(8), f'{defend:>4.1f}')
    # print('attack'.ljust(8), f'{attack:>4.1f}')

    return base + avail + attack + defend
