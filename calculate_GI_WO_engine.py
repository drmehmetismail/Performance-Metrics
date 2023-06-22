"""Calculate the Game Intelligence (GI) and Game Point Loss (GPL)
 for each game given the evals in the PGN file dump the data to a .json file."""

# Import the necessary libraries
import json
import os
import chess.pgn
from chess.engine import Cp, Mate, MateGiven, Wdl
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
        "counts": {
        "white_blunder": 0,
        "black_blunder": 0,
        "white_mistake": 0,
        "black_mistake": 0,
        "white_inaccuracy": 0,
        "black_inaccuracy": 0,
        }
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
    # If the scoring system is "Standard"
    if scoring_system == "Standard":
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


# Function to extract %eval from comments
def extract_eval_from_node(node):
    if node.eval():
        eval_value = node.eval().relative
        if eval_value.is_mate():
            # If it's a mate for us, return +10, if it's against us, return -10
            return 10 if eval_value.mate() > 0 else -10
        else:
            # Otherwise, convert from centipawns to full points
            return eval_value.score() / 100.0
    else:
        return None


# Function to calculate GI and GPL

def calculate_gi(move_number, game, white_gpl, black_gpl, white_gi, black_gi, white_move_number, black_move_number, scoring_system, counts):
    # Try to create a game from the current game
    node = game
    # Iterate through all the moves in the game
    while not node.is_end():
        premove_eval = extract_eval_from_node(node)
        if premove_eval is None:
            premove_eval = Cp(30)
        else:
            premove_eval = Cp(int(100*premove_eval))
        win_draw_loss = premove_eval.wdl()
        # print("premove: win_draw_loss",win_draw_loss)
        win_prob, draw_prob, loss_prob = win_draw_loss.wins / 1000, win_draw_loss.draws / 1000, win_draw_loss.losses / 1000
        turn = "White" if node.board().turn == chess.WHITE else "Black"
        premove_exp_white, premove_exp_black = calculate_expected_value(
            win_prob, draw_prob, loss_prob, turn, scoring_system)
        # Make the move on the board
        next_node = node.variation(0)
        #print("premove_eval", premove_eval)
        node = next_node
        # Get the %eval from the comment after the move
        postmove_eval = extract_eval_from_node(node)
        postmove_eval = Cp(int(100*postmove_eval))
        # Get the expectation for both players after making the move
        win_draw_loss = postmove_eval.wdl()
        # print("postmove: win_draw_loss",win_draw_loss)
        win_prob, draw_prob, loss_prob = win_draw_loss.wins / 1000, win_draw_loss.draws / 1000, win_draw_loss.losses / 1000
        turn = "White" if node.board().turn == chess.WHITE else "Black"
        postmove_exp_white, postmove_exp_black = calculate_expected_value(win_prob, draw_prob, loss_prob, turn, scoring_system)
        # If it's black's turn
        if node.board().turn == chess.BLACK:
            # Define expected point loss of white's move
            exp_white_point_loss = premove_exp_white - postmove_exp_white
            """print("exp_white_point_loss", exp_white_point_loss)
            print("premove_exp_white", premove_exp_white)
            print("postmove_exp_white", postmove_exp_white)
            print("premove_eval", premove_eval)
            print("postmove_eval", postmove_eval)"""
            # Update white's GPL
            white_gpl += exp_white_point_loss
            # Add blunder, mistake, inaccuracy
            if exp_white_point_loss >= 0.7:
                counts['white_blunder'] += 1
            elif exp_white_point_loss >= 0.4:
                counts['white_mistake'] += 1
            elif exp_white_point_loss >= 0.2:
                counts['white_inaccuracy'] += 1
            # Update white's move number
            white_move_number += 1
        else:
            # Define expected point loss of black's move
            exp_black_point_loss = premove_exp_black - postmove_exp_black
            # print("exp_black_point_loss",exp_black_point_loss)
            # Update black's GPL
            black_gpl += exp_black_point_loss
            if exp_black_point_loss >= 0.7:
                counts['black_blunder'] += 1
            elif exp_black_point_loss >= 0.4:
                counts['black_mistake'] += 1
            elif exp_black_point_loss >= 0.2:
                counts['black_inaccuracy'] += 1
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
                    black_gi = -black_gpl
                # If the scoring system is "Standard"
                else:
                    white_gi = 1 - white_gpl
                    black_gi = -black_gpl
            # If black won
            elif result == '0-1':
                # Calculate GI for both players
                if scoring_system == "NorwayChess":
                    black_gi = 3 - black_gpl
                    white_gi = -white_gpl
                # If the scoring system is "Standard"
                else:
                    black_gi = 1 - black_gpl
                    white_gi = -white_gpl
            elif result == '1/2-1/2':
                # If it's a draw, calculate GI for both players
                if scoring_system == "NorwayChess":
                    white_gi = 1.25 - white_gpl
                    black_gi = 1.25 - black_gpl
                # If the scoring system is "Standard"
                else:
                    white_gi = 0.5 - white_gpl
                    black_gi = 0.5 - black_gpl
        else:
            # Calculate (expected) GI for both players
            white_gi = postmove_exp_white - white_gpl
            black_gi = postmove_exp_black - black_gpl
    return white_gi, black_gi, white_gpl, black_gpl, white_move_number, black_move_number, counts

# Function to save the PGN file
def save_pgn_file(game, new_pgn_file):
    # Open the new PGN file in append mode
    with open(new_pgn_file, "a") as fgame:
        # Write the game to the file
        print(game, file=fgame)

# Function to update the JSON file
def update_json_file(json_file, white_gpl, black_gpl, white_move_number, black_move_number, white_gi, black_gi, game, counts):
    Result = game.headers.get("Result", None)
    if Result == '1-0':
        whiteResult = 1
        blackResult = 0
    elif Result == '0-1':
        whiteResult = 0
        blackResult = 1
    elif Result == '1/2-1/2':
        whiteResult = 0.5
        blackResult = 0.5
    else:
        whiteResult = '...'
        blackResult = '...'
    # Create a dictionary with the data to be saved
    
    date = None
    if "UTCDate" in game.headers:
        dates = game.headers["UTCDate"]
    elif "Date" in game.headers:
        dates = game.headers["Date"]
    
    white_avg_gpl = white_gpl / white_move_number
    black_avg_gpl = black_gpl / black_move_number
    
    data = {
        "white_gi": round(white_gi, 2),
        "black_gi": round(black_gi, 2),
        "white_gpl": round(white_gpl, 2),
        "black_gpl": round(black_gpl, 2),
        "white_move_number": white_move_number,
        "black_move_number": black_move_number,
        "White": game.headers.get("White", None),
        "Black": game.headers.get("Black", None),
        "Event": game.headers.get("Event", None),
        "Site": game.headers.get("Site", None),
        "Date": dates,
        "Round": game.headers.get("Round", None),
        "WhiteElo": game.headers.get("WhiteElo", None),
        "BlackElo": game.headers.get("BlackElo", None),
        "whiteResult": whiteResult,
        "blackResult": blackResult,
        "counts": counts
    }

    # Write the data to the JSON file
    with open(json_file, "w") as json_output_file:
        json.dump(data, json_output_file, indent=4)

# Main function
def main():
    folder = 'input_folder_path'
    output_directory = 'output_folder_path'
    os.makedirs(output_directory, exist_ok=True)
    # Set the scoring system: 'NorwayChess' or 'Standard'. NorwayChess uses (3, 1.25, 0) scoring system, while Standard system is (1, 0.5, 0)
    scoring_system = 'NorwayChess'

    # Get all the .pgn files in the folder
    pgn_files = [f for f in os.listdir(folder) if f.endswith('.pgn')]
    # print(pgn_files)
    # Iterate through each PGN file
    for pgn_file in pgn_files:
        # Remove the file extension and create JSON and new PGN file names
        new_file = pgn_file[:-4]
        json_file = os.path.join(output_directory, new_file + '.json')
        

        # Open the PGN file
        pgn = open(os.path.join(folder, pgn_file))

        # Load data from the JSON file
        data = load_json_file(json_file)
        white_gi = data['white_gi']
        black_gi = data['black_gi']
        white_gpl = data['white_gpl']
        black_gpl = data['black_gpl']
        white_move_number = data['white_move_number']
        black_move_number = data['black_move_number']
        counts = data['counts']

        # Initialize variables
        move_number = 0
        # Iterate through each game in the PGN file
        while True:
            game = chess.pgn.read_game(pgn)
            # print(game)
            if game is None:
                break

            # Calculate GI and GPL for the current game
            white_gi, black_gi, white_gpl, black_gpl, white_move_number, black_move_number, counts = calculate_gi(
                move_number, game, white_gpl, black_gpl, white_gi, black_gi, white_move_number, black_move_number, scoring_system, counts)

        # Read the game again
        game = chess.pgn.read_game(open(os.path.join(folder, pgn_file)))

        # Update the JSON file with the new data
        update_json_file(json_file, white_gpl, black_gpl, white_move_number, black_move_number, white_gi, black_gi, game, counts)


# Call the main function
if __name__ == "__main__":
    main()
