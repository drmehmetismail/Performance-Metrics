import re

def update_chess_string(s):
    parts = re.split(r'(\d+\.\s)', s)  # split by "number-dot-space", keeping delimiters
    for i in range(1, len(parts), 2):  # process only "number-dot-space" parts
        if i % 4 == 1:  # if it's a white move, keep it as is
            continue
        parts[i] = parts[i].replace('.', '...')  # if it's a black move, replace '.' with '...'
    return ''.join(parts)  # join the parts back together

def add_brackets(s):
    s = s.replace('{', '{[')
    s = s.replace('}', ']}')
    return s

def remove_dollar_content(s):
    return re.sub(r'\$.*?\}', '', s)

def remove_parentheses_content(s):
    return re.sub(r'\(.*?\)', '', s)

input_pgn = 'enter_path_here'

with open(input_pgn, 'r') as pgn_file:
    pgn_string = pgn_file.read()

pgn_string = add_brackets(pgn_string)
pgn_string = remove_parentheses_content(pgn_string)
pgn_string = remove_dollar_content(pgn_string)
corrected_pgn_string = update_chess_string(pgn_string)

output_pgn = 'enter_path_here'
with open(output_pgn, 'w') as pgn_file:
    pgn_file.write(corrected_pgn_string)
