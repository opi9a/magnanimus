from .domains import make_domains
from .scoring import score_piece

# get the empty-board domains (by square, by piece)
RAW_DOMAINS = make_domains()


class Piece():
    """
    Attrs:
        type, eg queen      # or have Queen class?
        color, eg white
        square, eg 5,3
        attacking, eg [('p', (1, 3)), ('n', (4,4))]
        protecting, eg [('p', (7, 3)), ('b', (5,5))]
        covering, eg [(6,3), (4,3), (3,3)..]

        score, based on attacking, protecting, covering (and inherent value)
    Methods:
        init with row, col etc
        _get raw domain # lookup with square, piece type
        _get attacking, protecting, covering
            - work out along raw domains, using board
        _get score

        move?
            new row, col
            new raw domain, attacking, protecting, covering
            effect on OTHERS attacking, protecting, covering
            (or recalc whole board)

    """
    def __init__(self, name, color, row, col, board):
        # unsure if I want square here or just use the piece's index / key
        self.name = name
        self.color = color
        self.square = row, col

        self.available = None
        self.attacking = None
        self.defending = None
        self.score = None

        if board is not None:
            self.calculate(board)


    def __repr__(self):
        out = [f"{k+' :'}".ljust(12) + str(v) for k, v in self.__dict__.items()
               if k not in ['col', 'row']]
        return "\n".join(out)

    def calculate(self, board):
        """
        Based on the piece's position and the rest of the board,
        get the domains available, attacking and defending

        Recalculate the score
        """
        a, b, c = get_actual_domains(self, board)
        self.available, self.attacking, self.defending = a, b, c

        self.score = score_piece(self)


def get_actual_domains(piece, board):
    """
    Return:
        attacking - list of (piece, square) tuples
        defending - list of (piece, square) tuples
        covering - list of squares
    """
    # directional

    if piece.name == 'pawn':
        p_name = piece.color[0] + '_pawn'
    else:
        p_name = piece.name

    raw_domains = RAW_DOMAINS[piece.square][p_name]

    available = []
    attacking = []
    defending = []

    if piece.name in ['rook', 'bishop', 'queen']:
        for direction in raw_domains:
            # work outwards
            for square in direction:
                if board[square] is None:
                    available.append(square)
                elif board[square].color == piece.color:
                    defending.append((board[square].name, square))
                    break
                else:
                    attacking.append((board[square].name, square))
                    break

    elif piece.name in ['king', 'knight']:
        for square in raw_domains:
            if board[square] is None:
                available.append(square)
            elif board[square].color == piece.color:
                defending.append((board[square].name, square))
            else:
                attacking.append((board[square].name, square))

    elif piece.name == 'pawn':
        for square in raw_domains['covering']:
            if board[square] is None:
                available.append(square)
            else:
                break

        for square in raw_domains['hitting']:
            if board[square] is None:
                continue
            elif board[square].color == piece.color:
                defending.append((board[square].name, square))
            else:
                attacking.append((board[square].name, square))


    return available, attacking, defending


