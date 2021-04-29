import stockfish

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
