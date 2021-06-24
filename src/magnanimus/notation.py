from .Piece import Piece

def trad_mv_to_vec(trad_mv, to_move, board_arr):
    """
    Eg Ne4: look for a unique knight that can move from e4 

    e4      : pawn
    Nf2     : knight
    Ndf2    : knight on d file
    N3f2    : knight on rank 3

    exd5    : pawn takes d5
    Nxd5    : knight takes d5
    Nfxd5   : knight on f file takes d5
    N3xd5   : knight on rank 3 takes d5


    0-0     : castles king side
    0-0-0   : castles queen side

    e8Q     : promote pawn to queen
    """

    parsed_mv = parse_trad_mv(trad_mv)

    # now get source piece, check legal etc


def parse_trad_mv(trad_mv):
    # deal with castling
    # (get rid of x)
    # get piece type to move
    # get dest square
    # identify source sq (using additional info if reqd)

    mv = trad_mv

    # neither capture nor check need to be explicit
    # though they can be
    if 'x' in mv:
        explicit_capture = True
        mv = mv.replace('x', '')
    else:
        explicit_capture = False

    if '+' in mv:
        explicit_check = True
        mv = mv.replace('+', '')
    else:
        explicit_check = False

    # special case: castling
    if mv[0] == '0':
        if '0' in mv[1:-1]:
            return 'castle_qside'
        return 'castle_kside'

    # special case: promotion
    if not mv[-1].isnumeric():
        if not mv[-2] == '8':
            raise ValueError(f'move {trad_mv}: cannot promote from here')
        promotion_to = mv[-1]
        mv = mv[:-1]
    else:
        promotion_to = None


    # if a capital its a piece - record and remove
    if mv[0].isupper():
        piece = mv[0]
        mv = mv[1:]
    else:
        piece = 'p'

    # now left with destination, and any identifier prepended
    if len(mv) == 3:
        identifier = mv[0]
        mv = mv[1:]
    else:
        identifier = None

    if not(len(mv) == 2 and mv[1].isnumeric() and mv[0].islower()):
        raise ValueError(f'cannot parse {trad_mv}')

    return {
        'piece': piece,
        'identifier': identifier,
        'promotion_to': promotion_to,
    }


    for row in range(8):
        for col in range(8):
            pass
            
    

