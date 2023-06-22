import os
import chess.pgn
import math

def scan_directory_for_pgn_files(directory):
    # Recursively walk through directory and subdirectories
    for folder_name, subfolders, file_names in os.walk(directory):
        for file_name in file_names:
            if file_name.endswith('.pgn'):
                file_path = os.path.join(folder_name, file_name)
                # Extract the subfolder name relative to the root directory
                relative_subfolder_name = os.path.relpath(folder_name, directory)
                scan_pgn_file_for_missing_eval(relative_subfolder_name, file_name, file_path)

def scan_pgn_file_for_missing_eval(subfolder_name, file_name, file_path):
    with open(file_path, 'r', encoding='utf-8') as pgn_file:
        game_number = 0
        while True:
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                # End of file
                break
            game_number += 1
            node = game
            move_number = 0
            while not node.is_end():
                move_number += 1
                node = node.next()
                # Check if '%eval' comment is present
                comment = node.comment
                if '%eval' not in comment:
                    print(f'Missing %eval in subfolder "{subfolder_name}", file "{file_name}", move {math.ceil(move_number/2)}')

# Example usage:
# Replace 'path_to_directory' with the path of your directory containing subfolders with PGN files
path_to_directory = 'path_here'
scan_directory_for_pgn_files(path_to_directory)
