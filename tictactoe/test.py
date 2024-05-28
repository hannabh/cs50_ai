import tictactoe as ttt

X = "X"
O = "O"
EMPTY = None

board = [[EMPTY, O, X],
        [EMPTY, X, EMPTY],
        [EMPTY, EMPTY, EMPTY]]
print(ttt.minimax(board))
