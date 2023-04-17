"""Calculate the Game Intelligence (GI) and Game Point Loss (GPL)
 for each game in a PGN file and dump the data to a .json file."""

# Import the necessary libraries
import json
import os
import chess.pgn
import chess.engine

# Function to load the JSON file
def load_json_file(json_file):
    default_data = {
        "white_gi": 0,
        "black_gi": 0,
        "white_gpl": 0,
        "black_gpl": 0,
        "white_move_number": 0,
        "black_move_number": 0,
    }
    try:
        # Read the JSON file
        with open(json_file) as json_input_file:
            data = json.load(json_input_file)
        # Ensure that all keys exist in the data dictionary
        for key in default_data.keys():
            if key not in data:
                data[key] = default_data[key]
        return data
    except FileNotFoundError:
        # Return default values if the file is not found
        return default_data

# Function to calculate the expected value of a position based on the scoring system
def calculate_expected_value(win_prob, draw_prob, loss_prob, turn, scoring_system):
    # If the scoring system is "FIDE"
    if scoring_system == "FIDE":
        # If it's white's turn
        if turn == "White":
            expected_value_white = win_prob*1 + draw_prob*0.5
            expected_value_black = loss_prob*1 + draw_prob*0.5
        # If it's black's turn
        else:
            expected_value_white = loss_prob*1 + draw_prob*0.5
            expected_value_black = win_prob*1 + draw_prob*0.5
    # If the scoring system is "NorwayChess"
    else:
        # If it's white's turn
        if turn == "White":
            expected_value_white = win_prob*3 + draw_prob*1.25
            expected_value_black = loss_prob*3 + draw_prob*1.25
        # If it's black's turn
        else:
            expected_value_white = loss_prob*3 + draw_prob*1.25
            expected_value_black = win_prob*3 + draw_prob*1.25
    # Return the expected value
    return expected_value_white, expected_value_black


# Function to calculate GI and GPL
def calculate_gi(move_number, target_move_number, game, engine, t, n, white_gpl, black_gpl, white_gi, black_gi, white_move_number, black_move_number, scoring_system):
    # Create a chess board from the current game
    board = game.board()

    # Iterate through all the moves in the game
    for move in game.mainline_moves():
        # If the current move number is less than the target move number
        if move_number < target_move_number:
            # Make the move on the board
            board.push(move)
            # Increment the move number
            move_number += 1
            # Skip to the next iteration
            continue
        else:
            # Analyze the current board position using the chess engine
            premove_info = engine.analyse(board, chess.engine.Limit(time=t, nodes=n))
            # Get the expectation for both players before making the move
            win_draw_loss = premove_info['score'].wdl()
            win_prob, draw_prob, loss_prob = win_draw_loss[0] /1000, win_draw_loss[1] /1000, win_draw_loss[2] /1000
            turn = "White" if board.turn == chess.WHITE else "Black"
            premove_exp_white, premove_exp_black = calculate_expected_value(win_prob, draw_prob, loss_prob, turn, scoring_system)  
            # Make the move on the board
            board.push(move)
            # Analyze the new board position using the chess engine
            postmove_info = engine.analyse(board, chess.engine.Limit(time=t, nodes=n))
            # Get the expectation for both players after making the move
            win_draw_loss = postmove_info['score'].wdl()
            win_prob, draw_prob, loss_prob = win_draw_loss[0] /1000, win_draw_loss[1] /1000, win_draw_loss[2]/1000
            turn = "White" if board.turn == chess.WHITE else "Black"
            postmove_exp_white, postmove_exp_black = calculate_expected_value(win_prob, draw_prob, loss_prob, turn, scoring_system)
            # If it's black's turn
            if board.turn == chess.BLACK:
                # Update white's GPL
                white_gpl += premove_exp_white - postmove_exp_white
                # Update white's move number
                white_move_number += 1
            else:
                # Update black's GPL
                black_gpl += premove_exp_black - postmove_exp_black
                # Update black's move number
                black_move_number += 1
            # Check if the game has a result
            if 'Result' in game.headers and game.headers['Result'] != '*':
                # Get the result of the game
                result = game.headers['Result']
                # If white won
                if result == '1-0':
                    # Calculate GI for both players
                    if scoring_system == "NorwayChess":
                        white_gi = 3 - white_gpl
                    # If the scoring system is "FIDE"
                    else:
                        white_gi = 1 - white_gpl
                    black_gi = -black_gpl
                # If black won
                elif result == '0-1':
                    # Calculate GI for both players
                    if scoring_system == "NorwayChess":
                        black_gi = 3 - black_gpl
                    # If the scoring system is "FIDE"
                    else:
                        black_gi = 1 - black_gpl
                    white_gi = -white_gpl
                else:
                    # If it's a draw, calculate GI for both players
                    if scoring_system == "NorwayChess":
                        white_gi = 1.25 - white_gpl
                        black_gi = 1.25 - black_gpl
                    # If the scoring system is "FIDE"
                    else:
                        white_gi = 0.5 - white_gpl
                        black_gi = 0.5 - black_gpl
            else:
                # Calculate (expected) GI for both players
                white_gi = postmove_exp_white - white_gpl
                black_gi = postmove_exp_black - black_gpl
    return white_gi, black_gi, white_gpl, black_gpl, white_move_number, black_move_number

# Function to save the PGN file
def save_pgn_file(game, new_pgn_file):
    # Open the new PGN file in append mode
    with open(new_pgn_file, "a") as fgame:
        # Write the game to the file
        print(game, file=fgame)

# Function to update the JSON file
def update_json_file(json_file, white_gpl, black_gpl, white_move_number, black_move_number, white_gi, black_gi):
    # Create a dictionary with the data to be saved
    data = {
        "white_gi": white_gi,
        "black_gi": black_gi,
        "white_gpl": white_gpl,
        "black_gpl": black_gpl,
        "white_move_number": white_move_number,
        "black_move_number": black_move_number,
    }

    # Write the data to the JSON file
    with open(json_file, "w") as json_output_file:
        json.dump(data, json_output_file, indent=4)

# Main function
def main():
    folder = '/workspaces/Performance-Metrics/Norway22'
    engine_path = '/home/linuxbrew/.linuxbrew/Cellar/stockfish/15.1/bin/stockfish'
    # Set engine limits d for depth, t for time, and n for nodes
    # d = 20
    t = 2
    n = None
    scoring_system = 'NorwayChess' # 'NorwayChess' or 'FIDE'

    # Get all the .pgn files in the folder
    pgn_files = [f for f in os.listdir(folder) if f.endswith('.pgn')]

    # Iterate through each PGN file
    for pgn_file in pgn_files:
        # Remove the file extension and create JSON and new PGN file names
        new_file = pgn_file[:-4]
        json_file = os.path.join(folder, new_file + '.json')
        new_pgn_file = new_file + '_gi.pgn'

        # Open the PGN file
        pgn = open(os.path.join(folder, pgn_file))
        # Initialize the chess engine
        engine = chess.engine.SimpleEngine.popen_uci(engine_path)

        # Load data from the JSON file
        data = load_json_file(json_file)
        white_gi = data['white_gi']
        black_gi = data['black_gi']
        white_gpl = data['white_gpl']
        black_gpl = data['black_gpl']
        white_move_number = data['white_move_number']
        black_move_number = data['black_move_number']

        # Initialize variables
        move_number = 0
        target_move_number = white_move_number + black_move_number

        # Iterate through each game in the PGN file
        while True:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break

            # Calculate GI and GPL for the current game
            white_gi, black_gi, white_gpl, black_gpl, white_move_number, black_move_number = calculate_gi(
                move_number, target_move_number, game, engine, t, n, white_gpl, black_gpl, white_gi, black_gi, white_move_number, black_move_number, scoring_system)

        # Read the game again
        game = chess.pgn.read_game(open(os.path.join(folder, pgn_file)))

        # Add GI data to the game headers if they exist
        game.headers["WhiteGI"] = f"{white_gi:.2f}"
        game.headers["BlackGI"] = f"{black_gi:.2f}"

        # Add GPL data to the game headers
        game.headers["WhiteGPL"] = f"{white_gpl:.2f}"
        game.headers["BlackGPL"] = f"{black_gpl:.2f}"

        # Save the game to the new PGN file
        save_pgn_file(game, new_pgn_file)
        # Update the JSON file with the new data
        update_json_file(json_file, white_gpl, black_gpl, white_move_number, black_move_number, white_gi, black_gi)

        # Close the chess engine
        engine.quit()

# Call the main function
if __name__ == "__main__":
    main()
