import pandas as pd
from datetime import datetime, timedelta

from .constants import LOG
from .utils import invert_color
from .analyse import analyse_board
from .scoring import CHECKMATE_SCORE, STALEMATE_SCORE
from .Position import Position

MAX_ITS = 3

# in dev
def get_best_move(position, max_its=None, return_positions=False):
    """
    Calculate future positions and return the best move
    """
    max_its = max_its or MAX_ITS

    # init the positions list
    positions = [position]
    original_to_move = position.to_move
    moves_made = len(position.moves)
    to_move = original_to_move

    i = 1
    while True:
        LOG.info(f'getting positions for it {i}, with {original_to_move} to move')
        positions = extend_positions(positions, to_move)

        # filter the positions
        positions = filter_positions(positions, i, to_move)
        to_move = invert_color(to_move)

        if i == max_its:
            break

        i += 1


#     if best_position.mate and best_position.checked:
#         # if the best move is mate then its over
#         print(f'It is mate, returning None best move for {to_move}')
#         best_move = None
#     else:
#         best_move = best_position.moves[0]

    if not positions:
        return 'checkmate', None

    # need to re-sort, as will be ordered by the last to_move
    positions.sort(key=lambda x: x.score, reverse=original_to_move=='white')

    # because of zero indexing, the first NEXT move is at moves_made in list
    best_move = positions[0].moves[moves_made]

    if return_positions:
        return best_move, positions

    return best_move


def filter_positions(positions, i, last_to_move):
    """
    Depending on how many iterations, remove positions that are unlikely to 
    be followed by opponent, or choose not to follow for me
    """
    N_TO_RETURN = 500

    positions.sort(key=lambda x: x.score, reverse=last_to_move=='white')
    # discard all mates except 1

    if positions[0].mated and positions[0].checked == last_to_move:
        LOG.info('Mate inevitable on this position')
        return [positions[0]]

    LOG.info(f'going to return {min(N_TO_RETURN, len(positions))}')
    return positions[:N_TO_RETURN]


def extend_positions(positions, timeout=None, sec_to_think=1,
                 npositions_to_follow=5):
    """
    Return a list of positions that extend the one passed.
    Identify mates
    """

    if timeout is None:
        timeout = datetime.now() + timedelta(seconds=sec_to_think)

    positions_out = []

    # iterate over each existing position, spawning new ones from its next_moves
    for i,position in enumerate(positions):

        # TODO review this
        if position.mated:
            positions_out.append(position)
            continue

        # collect the new positions from this position, before deciding
        # whether to append to the main list
        child_positions = []

        # helpful later to know if they started off in check
        if position.to_move == position.checked:
            already_in_check = True
        else:
            already_in_check = False

        LOG.info(f'extending position {i+1} / {len(positions)}, {position.to_move} to move,'
                 f' {"they ARE" if position.checked else "NOT"} in check')

        for move in position.next_moves:
            new_position = Position(prev_posn=position, new_move=move)
            # need to get who is checked
            # if its last_to_move, reject
            if new_position.checked is not None:
                if position.to_move in new_position.checked:
                    LOG.info(f'dropping {move}: self check for {position.to_move}')
                    # not a legit move
                    continue
            else:
                child_positions.append(new_position)

        if not child_positions:
            # no options so mate of some kind
            # -> append a mated position
            if already_in_check:
                # mate for the opponent
                position.mated = position.to_move
            else:
                # stalemate
                position.mated = 'stalemate'

            position.next_moves = None
            positions_out.append(position)

        else:
            positions_out.extend(child_positions)

    # TODO select positions to follow

    return positions_out


