import chess.pgn
import chess.engine

class ChessAnalyzer:
    def __init__(self, engine_path, pgn_file, new_pgn_file, t=None, n=None, d=None):
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        self.pgn_file = pgn_file
        self.new_pgn_file = new_pgn_file
        self.t = t
        self.n = n
        self.d = d
        self.w_gpl = 0
        self.b_gpl = 0
        self.w_moves = 0
        self.b_moves = 0
        self.w_ga = 0
        self.b_ga = 0
        self.w_movesa = 0
        self.b_movesa = 0

    def update_gpl(self, pgn):
        while True:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break

            board = game.board()
            for move in game.mainline_moves():
                premove_info = self.engine.analyse(board, chess.engine.Limit(time=self.t, nodes=self.n, depth=self.d))
                
                if board.turn == chess.WHITE:
                    premove_exp_w = premove_info['score'].white().wdl().expectation()
                else:
                    premove_exp_b = premove_info['score'].black().wdl().expectation()
                board.push(move)
                postmove_info = self.engine.analyse(board, chess.engine.Limit(time=self.t, nodes=self.n, depth=self.d))
                postmove_wexp = postmove_info['score'].white().wdl().expectation()
                postmove_bexp = postmove_info['score'].black().wdl().expectation()

                if board.turn == chess.BLACK:
                    self.w_gpl += premove_exp_w - postmove_wexp
                    self.w_moves += 1
                    if premove_exp_w != 0:
                        self.w_ga += postmove_wexp / premove_exp_w
                        self.w_movesa += 1
                else:
                    self.b_gpl += premove_exp_b - postmove_bexp
                    self.b_moves += 1
                    if premove_exp_b != 0:
                        self.b_ga += postmove_bexp / premove_exp_b
                        self.b_movesa += 1

    def save_results(self):
        with open(self.pgn_file) as f:
            game = chess.pgn.read_game(f)
        result = game.headers['Result']

        if result in ['1-0', '0-1', '1/2-1/2']:
            if result == '1-0':
                w_gi = 1 - self.w_gpl
                b_gi = -self.b_gpl
            elif result == '0-1':
                w_gi = -self.w_gpl
                b_gi = 1 - self.b_gpl
            else:
                w_gi = 0.5 - self.w_gpl
                b_gi = 0.5 - self.b_gpl

            game.headers["WhiteGI"] = f"{w_gi:.2f}"
            game.headers["BlackGI"] = f"{b_gi:.2f}"

        w_agpl = self.w_gpl / self.w_moves
        b_agpl = self.b_gpl / self.b_moves
        w_aga = self.w_ga / self.w_movesa
        b_aga = self.b_ga / self.b_movesa

        game.headers["WhiteGPL"] = f"{self.w_gpl:.2f}"
        game.headers["BlackGPL"] = f"{self.b_gpl:.2f}"
        game.headers["WhiteAGPL"] = f"{w_agpl:.2f}"
        game.headers["BlackAGPL"] = f"{b_agpl:.2f}"
        game.headers["WhiteAccuracy"] = f"{w_aga:.2f}"
        game.headers["BlackAccuracy"] = f"{b_aga:.2f}"

        with open(self.new_pgn_file, "a") as fgame:
            print(game, file=fgame)


    def run(self):
        with open(self.pgn_file) as pgn:
            self.update_gpl(pgn)
        self.save_results()

    def close(self):
        self.engine.quit()

if __name__ == "__main__":
    t = set_time
    d = set_depth
    n = set_nodes
    new_file = 'PGN_file_goes_here'
    pgn_file = new_file + '.pgn'
    new_pgn_file = new_file + '_gi.pgn'
    engine_path = 'engine_path_goes_here'

    analyzer = ChessAnalyzer(engine_path, pgn_file, new_pgn_file, t=t, n=n, d=d)
    analyzer.run()
    analyzer.close()
