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
    'avail': 0.02,
    'defending': 0.05,
    'attacking': 0.02, # NB this multiplies the points value of attacked piece
    'check': 1,
}

def score_piece(piece, df):
    """
    Score from a pd series, and if gives check
    """
    base = PIECE_BASE_VALUES[piece.piece]
    avail, attack, defend = 0, 0, 0


    # available may be a nested list, so flatten (row, col for each)
    if piece.available is not None:
        avail = COEFFS['avail'] * len(np.array(piece.available).flatten()) / 2

    if piece.defending is not None:
        defend = COEFFS['defending'] * len(piece.defending)

    gives_check = False
    if piece.attacking is not None:
        attack = 0
        for square in piece.attacking:
            target = df.loc[square, 'piece']
            if target == 'king':
                gives_check = True
            else:
                attack += PIECE_BASE_VALUES[target] * COEFFS['attacking']

    # print('score for'.ljust(8), piece.color, piece.name)
    # print('base'.ljust(8), f'{base:>4.1f}')
    # print('avail'.ljust(8), f'{avail:>4.1f}')
    # print('defend'.ljust(8), f'{defend:>4.1f}')
    # print('attack'.ljust(8), f'{attack:>4.1f}')

    if piece.color == 'black':
        return - (base + avail + attack + defend), gives_check

    return base + avail + attack + defend, gives_check


