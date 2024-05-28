"""
Tic Tac Toe Player
"""

import copy
import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    turn_count = 0
    for row in board:
        turn_count += len(list(filter(None, row)))
    if turn_count % 2 == 0:
        return "X"  # returning X won't print in runner.py
    else:
        return "O"


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] is EMPTY:
                actions.add((i, j))
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action not in actions(board):
        raise Exception("Not a valid action for the given board")
    
    current_player = player(board)
    new_board = copy.deepcopy(board)
    new_board[action[0]][action[1]] = current_player
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    flat_list = [move for row in board for move in row]
    winning_positions = [[0,1,2], [3,4,5], [6,7,8], [0,3,6], [1,4,7], [2,5,8], [0,4,8], [2,4,6]]
    for p in winning_positions:
        if flat_list[p[0]] == flat_list[p[1]] == flat_list[p[2]] == X:
            return X
        elif flat_list[p[0]] == flat_list[p[1]] == flat_list[p[2]] == O:
            return O
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True
    elif not any(EMPTY in row for row in board):
        return True
    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    game_winner = winner(board)
    if game_winner == X:
        return 1
    elif game_winner == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board
    """
    if terminal(board):
        return None
    
    current_player = player(board)

    if current_player == X:
        best_score, best_action = max_value(board)
    else:
        best_score, best_action = min_value(board)
    
    return best_action


def max_value(board):
    """
    Recursively simulates all possible games from current state until reach a terminal state
    Returns the terminal state with maximum utility and corresponding action
    """
    max_value = -math.inf
    best_move = None

    if terminal(board):
        return utility(board), None
    
    for action in actions(board):
        val, _ = min_value(result(board, action)) 
        if val > max_value:
            max_value = val
            best_move = action
        if val == 1:  # alpha-beta pruning: max utility possible is 1
            break

    return max_value, best_move


def min_value(board):
    """
    Recursively simulates all possible games from current state until reach a terminal state
    Returns the terminal state with minimum utility and corresponding action
    """
    min_value = math.inf
    best_move = None

    if terminal(board):
        return utility(board), None
    
    for action in actions(board):
        val, _ = max_value(result(board, action))
        if val < min_value:
            min_value = val
            best_move = action
        if val == -1:  # alpha-beta pruning: min utility possible is -1
            break

    return min_value, best_move
