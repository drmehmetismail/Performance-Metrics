import chess.pgn
import os

# Define the directory where your PGN file is located
pgn_file = 'pgn_path_here'

# Define the directories where you want to write the new PGN files
output_directory_classical = 'output_folder_path_here'
output_directory_armageddon = 'output_folder_path_here'

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
        if 'Round' in game.headers and 'Board' in game.headers:
            round_str = game.headers['Round']
            board_str = game.headers['Board']

            # Check if the round and board are integers
            if not round_str.isdigit() or not board_str.isdigit():
                print(f"Skipping game with non-numeric Round or Board: Round={round_str}, Board={board_str}")
                continue

            # Convert the round and board to integers
            round = int(round_str)
            board = int(board_str)

            # Modify the Round header to include the Board number
            game.headers['Round'] = f'{round}.{board}'
        else:
            print("Skipping game with missing Round or Board header.")
            continue

        # If 'UTCDate' exists in the headers, copy its value to 'Date'
        if 'UTCDate' in game.headers:
            game.headers['Date'] = game.headers['UTCDate']

        # Determine the output directory based on whether the round is odd or even
        if round % 2 == 0:
            output_directory = output_directory_armageddon
        else:
            output_directory = output_directory_classical

        # Update round number
        round = (round + 1) // 2
        # Write the game to a new PGN file in the appropriate directory
        with open(os.path.join(output_directory, f'gameR{round}B{board}.pgn'), 'w') as output_file:
            exporter = chess.pgn.FileExporter(output_file)
            game.accept(exporter)
