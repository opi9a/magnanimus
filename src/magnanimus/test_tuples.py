SIMPLES = [
    ('knight', 'black', 0),
    ('king', 'white', 16),
]
KINGS_ONLY = [
    ('king', 'black', 0),
    ('king', 'white', 63),
]
IN_CHECK = [
    ('king', 'black', 0),
    ('king', 'white', 63),
    ('rook', 'white', 7),
]
CHECK_IMMINENT = [
    ('king', 'black', 0),
    ('king', 'white', 63),
    ('rook', 'white', 11),
]
CHECKMATE_IMMINENT = [
    ('king', 'black', 7),
    ('rook', 'white', 8),
    ('rook', 'white', 9),
    ('pawn', 'white', 16),
    ('pawn', 'white', 17),
]
