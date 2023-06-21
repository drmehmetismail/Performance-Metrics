import chess.pgn
import os

# Define the directory where your PGN file is located
pgn_file = 'pgn_path_here'

# Define the directories where you want to write the new PGN files
output_directory_classical = 'output_folder_path_here'

# Create the directories if they don't exist
os.makedirs(output_directory_classical, exist_ok=True)

# Open the multi-game PGN file
with open(os.path.join(pgn_file)) as pgn_file:
    while True:
        # Read the next game from the PGN file
        game = chess.pgn.read_game(pgn_file)

        # If no game is read, then we're done
        if game is None:
            break

        # Check if 'Round' and 'Board' exist in game headers
        round_str = game.headers.get('Round')
        board_str = game.headers.get('Board')
        
        # Initialize the filename
        filename = None

        # Check if the round and board are integers
        if round_str is not None and round_str.isdigit() and \
           board_str is not None and board_str.isdigit():
            # Convert the round and board to integers
            round = int(round_str)
            board = int(board_str)

            # Modify the Round header to include the Board number
            game.headers['Round'] = f'{round}.{board}'
            
            # Determine the output directory
            output_directory = output_directory_classical

            # Update round number
            round = (round + 1) // 2
            
            # Set the filename
            filename = f'gameR{round}B{board}.pgn'
        elif round_str is not None and round_str.isdigit():
            # Convert the round to integer
            round = int(round_str)
            
            # Determine the output directory
            output_directory = output_directory_classical
                
            # Update round number
            round = (round + 1) // 2
            
            # Set the filename
            filename = f'gameR{round}.pgn'
        else:
            # Extract White and Black players
            white = game.headers.get('White', 'unknown')
            black = game.headers.get('Black', 'unknown')
            
            # Default directory when round is missing
            output_directory = output_directory_classical
            
            # Set the filename
            filename = f'game{white}{black}.pgn'

        # If 'UTCDate' exists in the headers, copy its value to 'Date'
        if 'UTCDate' in game.headers:
            game.headers['Date'] = game.headers['UTCDate']

        # Write the game to a new PGN file in the appropriate directory
        with open(os.path.join(output_directory, filename), 'w') as output_file:
            exporter = chess.pgn.FileExporter(output_file)
            game.accept(exporter)
