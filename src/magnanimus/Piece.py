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

    """
    def __init__(self, board_arr, row, col, threatened_domain):
        # unsure if I want square here or just use the piece's index / key
        self.board_arr = board_arr
        self.square = row, col
        self.threatened_domain = threatened_domain

        self.color, self.name = board_arr[row, col]

        a, b, c = get_actual_domains(self, board_arr, threatened_domain)
        self.available, self.attacking, self.defending = a, b, c
        self.next_moves = self.available + [x[1] for x in self.attacking]

        self.score = score_piece(self)


    def __repr__(self):
        pad = 12
        sq = self.square
        out = ['square:'.ljust(pad) + f'{sq[0]}, {sq[1]}']
        for field in ['available', 'attacking', 'defending', 'next_moves']:
            out.append(f'{field}:'.ljust(pad) + f'{self.__dict__[field]}')
        out.append('score:'.ljust(pad) + f'{self.score:.3f}')
        return "\n".join(out)


def get_actual_domains(piece, board, threatened_domain):
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
                elif board[square][0] == piece.color:
                    defending.append((board[square][1], square))
                    break
                else:
                    attacking.append((board[square][1], square))
                    break

    elif piece.name  == 'knight':
        for square in raw_domains:
            if board[square] is None:
                available.append(square)
            elif board[square][0] == piece.color:
                defending.append((board[square][1], square))
            else:
                attacking.append((board[square][1], square))

    elif piece.name == 'pawn':
        for square in raw_domains['covering']:
            if board[square] is None:
                available.append(square)
            else:
                break

        for square in raw_domains['hitting']:
            if board[square] is None:
                continue
            elif board[square][0] == piece.color:
                defending.append((board[square][1], square))
            else:
                attacking.append((board[square][1], square))

    elif piece.name  == 'king':
        breakpoint()
        if threatened_domain is None:
            threatened_domain = []
        for square in raw_domains:
            if board[square] is None and square not in threatened_domain:
                available.append(square)
            elif board[square][0] == piece.color:
                defending.append((board[square][1], square))
            else:
                attacking.append((board[square][1], square))


    return available, attacking, defending


