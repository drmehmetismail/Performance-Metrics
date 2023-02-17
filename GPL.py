import chess
import chess.pgn
import chess.engine
from chess.engine import Cp, Mate, MateGiven


# Load the PGN file
pgn = open('carlsen-wang.pgn')

# Initialize the engine
engine = chess.engine.SimpleEngine.popen_uci('/home/linuxbrew/.linuxbrew/Cellar/stockfish/15.1/bin/stockfish')

# Set engine limits d for depth, t for time, and n for nodes
d = 20
t = 1
n = 1000

# Initialize counters for white and black's total centipawn loss
w_tel = 0
b_tel = 0

# Initialize counters for white and black's total moves
w_moves = 0
b_moves = 0

# Loop through each game in the PGN file
while True:
    #print(game)
    game = chess.pgn.read_game(pgn)
    #print(game)
    if game is None:
        break

    # Play through the game using the engine
    board = game.board()
    for move in game.mainline_moves():
        # Info before the move
        b_info = engine.analyse(board, chess.engine.Limit(time=t))
        if board.turn == chess.WHITE:
            b_exp = b_info['score'].white().wdl().expectation()
        else:
            b_exp = b_info['score'].black().wdl().expectation()
        board.push(move)
        # Update the TEL and move counters: Info after the move
        a_info = engine.analyse(board, chess.engine.Limit(time=t))
        if board.turn == chess.BLACK:
            w_tel += b_exp-a_info['score'].white().wdl().expectation()
            w_moves += 1
        else:
            b_tel += b_exp-a_info['score'].black().wdl().expectation()
            b_moves += 1
            
# Calculate the average centipawn loss for each player
w_atel = w_tel / w_moves
b_atel = b_tel / b_moves

    
# Add the TEL headers in the game
with open('carlsen-wang.pgn') as f:
    game = chess.pgn.read_game(f)
game.headers["TEL_W"] = f": {w_tel:.2f}"
game.headers["TEL_B"] = f": {b_tel:.2f}"
game.headers["ATEL_W"] = f": {w_atel:.2f}"
game.headers["ATEL_B"] = f": {b_atel:.2f}"

# Print the results
print("White TEL:", w_tel)
print("Black TEL:", b_tel)

print("White ATEL:", w_atel)
print("Black ATEL:", b_atel)

# Save the PGN file with the TELs as headers
print(game)
with open("carlsen-wang_tel.pgn", "a") as fgame:
 print(game, file=fgame)

# Close the engine
engine.quit()