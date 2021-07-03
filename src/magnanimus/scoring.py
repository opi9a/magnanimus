PIECE_BASE_VALUES = {
    'pawn': 1,
    'bishop': 3,
    'knight': 3,
    'rook': 5,
    'queen': 9,
    'king': 0,
}

COEFFS = {
    'free': 0.02,
    'defending': 0.05,
    'attacking': 0.02, # NB this multiplies the points value of attacked piece
    'check': 1,
}

CHECKMATE_SCORE = 999
STALEMATE_SCORE = 0

