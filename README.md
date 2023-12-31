# Chess Metrics

This project includes chess metrics for calculating "game intelligence". The focus is mostly on chess but other games will also be included.

This is a Python script that calculates the Game Intelligence (GI) and Game Point Loss (GPL) for a given PGN file using the python-chess library and a chess engine (e.g. Stockfish).

# Requirements
To use this script, you will need to have the following installed:

Python 3 (https://www.python.org/downloads/)
python-chess library (https://pypi.org/project/python-chess/)
Stockfish engine (https://stockfishchess.org/download/)

# Usage

Place your PGN file in the same directory as the GI.py script.
The script will play through each move in the PGN file, calculate the GI, GPL (and AGPL) for each player, and print out the results.
The script will also write the results as a header in the PGN file and save it as a new file.

# License
This script is released under the GPL-3.0 License. See LICENSE for more information.

# Description of the metrics
GI is a metric to evaluate a player's "intelligence" in a "gamingproof" way by a strong chess AI in a game. 

As is standard, a win in a chess game is worth 1 point, a draw is worth 1/2 points, and a loss is worth 0 points. The game point loss is the number of potential points a player loses by making moves compared to the engine win/draw/loss probabilities (or human win/draw/loss probabilities).

For example, if a player is in a winning position and makes a losing move, they lose 1 game point. If they are in a position to win but make a move that leads to a draw, they lose 0.5 game points on average. The GPL for a player in a game is the some of each move game point losses.

The average game point loss is the GPL divided by the number of moves a player has made in the game. This gives an idea of how well a player is playing and how many potential points they are losing per move.

Formally, let L_1 denote the loss of White (player 1) by a move, w^* and d^* denote the win probability of White when White plays the best (or perfect) move in a position. Similarly, w and d denote the win probability of White after White’s actual move. Then, we have the following definition.
L_1   = 1w^* + 0.5^* - 1w - 0.5d

Game Point Loss (aka TEL)
GPL of a player is simply the sum of the losses of a player during a game. GPL of White is:
GPL_1  = L_1 (1)+L_1 (2)+⋯+L_1 (last move n)
Similarly, GPL of Black is: 
GPL_2  = L_2 (1)+L_2 (2)+⋯+L_2 (last move m)
Sometimes White and Black make the same number of moves but it could be that White makes one more or less move than black. 

The GI of each player is defined as follows. Let $r_i$ denote the points that player $i$ receives from the game, where $r_i$ can be 1 if player $i$ wins, 0.5 if the game ends in a draw, and 0 if player $i$ loses. Then, the game intelligence (GI) of player $i$ is defined as the difference between the points received by player $i$ and their GPL, i.e., GI_i = r_i - GPL_i. For more information, see https://doi.org/10.48550/arXiv.2302.13937

Average GPL
Average GPL of White is AGPL_1=(GPL_1)/n and for Black is AGPL_2=(GPL_2)/m.
AGPL tells us how players performed on average (per move). 


Tournament (Total) GPL
This is simply defined by summing up every GPL of a player in the past games played in a tournament (or in a series of games).

## Citation
Please cite the following paper if you find this helpful.
```
@article{ismail2023human,
  title={Human and Machine: Practicable Mechanisms for Measuring Performance in Partial Information Games},
  author={Ismail, Mehmet S},
  journal={arXiv preprint arXiv:2302.13937},
  year={2023}
}
```

