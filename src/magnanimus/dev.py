
"""
Keep a tree structure

Each node:
    board info  - can be a df as below
    parent
    path
    child moves
    scores for each piece

board_df:
    index: (row, col) tuples
    cols: 'color', 'piece', 'available', attacking', 'defending', 'score'
    (may need something for check)

paths_df:
    still need to keep track of the paths evaluated etc
    when 1 is done, record salient in a df
    index: path
    cols: score (check etc??) (to_move?)
"""
import pandas as pd


