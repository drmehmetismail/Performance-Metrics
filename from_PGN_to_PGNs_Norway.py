"""This script is for Norway Chess games played in 2019 and later"""
import chess.pgn
import os

# Define the directory where your PGN file is located
pgn_file = 'pgn_path_here'

# Define the directories where you want to write the new PGN files
output_directory_classical = '/output_folder_path_here/NorwayChess{year}'
output_directory_armageddon = '/output_folder_path_here/NorwayChess{year}armageddon'

# Create the directories if they don't exist
os.makedirs(output_directory_classical, exist_ok=True)
os.makedirs(output_directory_armageddon, exist_ok=True)

# Open the multi-game PGN file
with open(os.path.join(pgn_file)) as pgn_file:
    while True:
        # Read the next game from the PGN file
        game = chess.pgn.read_game(pgn_file)
        # print("Game:", game)
        # If no game is read, then we're done
        if game is None:
            break

        # Check if 'Round' and 'Board' exist in game headers
        round_str = game.headers.get('Round', '')
        board_str = game.headers.get('Board', '')

        # Check if the round and board are integers
        if not round_str.isdigit() and not board_str.isdigit():
            filename = f'game{game.headers["White"]}{game.headers["Black"]}.pgn'
        elif not board_str.isdigit():
            round = int(round_str)
            # Update round number
            round_updated = (round + 1) // 2
            filename = f'gameR{round_updated}.pgn'
        else:
            round = int(round_str)
            # Update round number
            round_updated = (round + 1) // 2
            board = int(board_str)
            filename = f'gameR{round_updated}B{board}.pgn'

        # If 'UTCDate' exists in the headers, copy its value to 'Date'
        if 'UTCDate' in game.headers:
            game.headers['Date'] = game.headers['UTCDate']

        # Determine the output directory based on whether the round is odd or even
        output_directory = output_directory_armageddon if round % 2 == 0 else output_directory_classical


        # Write the game to a new PGN file in the appropriate directory
        with open(os.path.join(output_directory, filename), 'w') as output_file:
            exporter = chess.pgn.FileExporter(output_file)
            game.accept(exporter)
