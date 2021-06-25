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
    def __init__(self, board_df, row, col):
        # unsure if I want square here or just use the piece's index / key
        self.board_df = board_df
        self.square = row, col

        self.name , self.color= board_df.loc[(row, col)].values

        a, b, c = get_actual_domains(self.square, board_df)
        self.available, self.attacking, self.defending = a, b, c
        self.next_moves = self.available + [x[1] for x in self.attacking]

        if 'king' in [x[0] for x in self.attacking]:
            self.gives_check = True
        else:
            self.gives_check = False

        self.score = score_piece(self)


    def __repr__(self):
        pad = 16
        sq = self.square
        out = ['square:'.ljust(pad) + f'{sq[0]}, {sq[1]}']
        for field in ['color', 'name', 'available', 'attacking', 'defending',
                      'next_moves', 'gives_check']:
            out.append(f'{field}:'.ljust(pad) + f'{self.__dict__[field]}')
        out.append('score:'.ljust(pad) + f'{self.score:.3f}')
        return "\n".join(out)


