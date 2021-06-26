import stockfish
import chess
import chess.engine
import chess.pgn


def test_stockfish_evaluation():
    stockfish_defaults = {
        "Write Debug Log": "false",
        "Contempt": 0,
        "Min Split Depth": 0,
        "Threads": 1,
        "Ponder": "false",
        "Hash": 16,
        "MultiPV": 1,
        "Skill Level": 20,
        "Move Overhead": 30,
        "Minimum Thinking Time": 20,
        "Slow Mover": 80,
        "UCI_Chess960": "false",
    }

    engine = stockfish.Stockfish(path="C:\Program Files (x86)\Tarrasch\Engines\stockfish_11_x64.exe", parameters={"Threads": 6, "Hash": 1024, "Minimum Thinking Time": 30})
    engine.set_fen_position("rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")
    engine.set_depth(30)

    print(engine.get_best_move())

    print(engine.get_evaluation())

# candidate useful thing
def test_python_chess_evaluation(fen, depth=20, moves=5):
    engine = chess.engine.SimpleEngine.popen_uci("C:\Program Files (x86)\Tarrasch\Engines\stockfish_11_x64.exe")
    try:
        board = chess.Board(fen)

        info = engine.analyse(board, chess.engine.Limit(depth=depth), multipv=moves)
        print(info)
        for x in info:
            print(x['multipv'])
            print(x['score'])
            print(x['pv'])
    finally:
        engine.quit()


def open_pgn():
    pgn = open("wombathammer_2021_03.pgn")

    game = chess.pgn.read_game(pgn)
    while game is not None:
        board = game.board()

        print(game)
        for move in game.mainline_moves():
            board.push(move)
            print(move)
            print(board.fen())

        game = chess.pgn.read_game(pgn)


if __name__ == "__main__":
    # test_python_chess_evaluation("rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2", 20, 10)
    open_pgn()
