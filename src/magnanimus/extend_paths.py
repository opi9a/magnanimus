import pandas as pd
from datetime import datetime, timedelta

from .constants import LOG, PATHS_DF_COLS
from .utils import update_board, invert_color
from .analyse_board import analyse_board

def extend_paths(board_arr, paths_df, timeout=None, sec_to_think=1,
                 npaths_to_follow=5):
    """
    Take a paths_df and return an extended version.

    path            score   to_move   next_moves
    ====            =====   =======   ==========
    [((0,0),(5,5))]   3.4    'black'  [((5,5),(7,5)), ((5,5),(6,5))..]
    [((0,0),(5,4))]   3.8    'black'  [((5,4),(7,4)), ((5,4),(6,4))..]
                                      
    (return df with same structure but (more and) longer paths, new scores
     and new next_moves)

    path                           score   to_move   next_moves
    ====                           =====   =======   ==========
    [((0,0),(5,5)), ((5,5),(7,5))]   7.5    'white'  [((7,5),(0,5))..]
    [((0,0),(5,5)), ((5,5),(6,5))]   2.4    'white'  [((6,5),(0,5))..]
    ...
    [((0,0),(5,4)), ((5,4),(7,4))]   3.1    'white'  [((7,4),(0,4))..]

    Create a new df with the extended paths.
    If timeout, append the old (un-extended) to it

    paths_out = []
    For each path:
        for each next move:
            make a board
            get score
            get next_moves
            add to paths_out
    make a new paths_df from paths_out
    append any unprocessed
    """

    if timeout is None:
        timeout = datetime.now() + timedelta(seconds=sec_to_think)

    next_moves_to_try = paths_df['next_moves'].apply(len).sum()
    ext_round  = len(paths_df['path'][0])
    next_moves_tried = 0

    paths_out = []

    # iterate over each existing path, spawning new ones from its next_moves
    for i, path, score, to_move, next_moves in paths_df.itertuples():

        # ordinarily will be a set of next moves but in case (eg in debug)
        if next_moves is None:
            _, _, next_moves, _ = analyse_board(board_arr, to_move=to_move)

        # make a board_arr for the passed path (cd be multiple moves)
        root_board = update_board(board_arr, path)

        next_paths = []
        for move in next_moves:
            # make a board_arr to simulate the move and record its data
            # NB want the NEXT moves from the NEXT player
            board_from_move = update_board(root_board, [move])
            scores, score, next_moves, is_checked = analyse_board(
                board_from_move, invert_color(to_move))

            if is_checked == to_move:
                LOG.info(f'{move} by {to_move} would leave in check')
                continue
            
            # note the appended path has the opposite color to move
            next_paths.append({
                'path': path + list([move]),
                'score': score,
                'to_move': invert_color(to_move),
                'next_moves': next_moves,
            })

        next_moves_tried += len(next_moves)
        LOG.info(f'for round {ext_round}, in path {i} / {len(paths_df)} '
                 f'tried {next_moves_tried} / {next_moves_to_try}')


        # return next_paths
        # filter to get the best moves for the player concerned
        next_paths_df = pd.DataFrame(next_paths)
        paths_out.append(next_paths_df)
                         # .sort_values(key=get_move_goodness, ascending=False)
                         # .head(npaths_to_follow))


    if not paths_out:
        print('checkmate')
        return None

    df = pd.concat(paths_out)

    if i + 1 < len(paths_df):
        df = df.append(paths_df.iloc[i+1:])

    return df

def get_move_goodness(path_entry):
    """
    Return a measure of move goodness which reflects the color playing.
    - i.e. if 'black' then more negative is better
    """
    if path_entry['to_move'] == 'black':
        return path_entry['score'] * -1
    return path_entry['score']



