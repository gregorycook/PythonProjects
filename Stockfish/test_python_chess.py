import chess
import chess.engine
import chess.pgn
import os
import sqlite3

import chessdotcom

def engine_plays_itself():
    engine = chess.engine.SimpleEngine.popen_uci("C:\Program Files (x86)\Tarrasch\Engines\stockfish_11_x64.exe")

    board = chess.Board()
    while not board.is_game_over():
        result = engine.play(board, chess.engine.Limit(time=0.1))
        print(result)
        print(result.info)
        board.push(result.move)

    print(board)

    engine.quit()


def open_pgn():
    pgn = open("EricsGame.pgn")

    game = chess.pgn.read_game(pgn)
    while game is not None:
        board = game.board()

        for move in game.mainline_moves():
            board.push(move)
            print(board.fen())

        game = chess.pgn.read_game(pgn)


def engine_analyze_position():
    engine = chess.engine.SimpleEngine.popen_uci("C:\Program Files (x86)\Tarrasch\Engines\stockfish_11_x64.exe")
    engine.configure({"Hash": 2048, "Threads": 8})

    board = chess.Board("r1b1k1nr/p1q1ppbp/2pp2p1/2p5/4PP2/2NP1N2/PPP3PP/R1BQ1RK1 b kq - 0 8")
    info = engine.analyse(board, chess.engine.Limit(depth=40))
    print("Score:", info["score"])
    # Score: PovScore(Mate(+1), WHITE)

    engine.quit()


def parse_big_pgn_file():
    pgn = open("last2000.pgn")

    connection = sqlite3.connect("chess.db")
    insert_game = "INSERT INTO game (id, white, black, result) VALUES(?, ?, ?, ?)"
    insert_FEN = "INSERT INTO FEN (id, FEN) VALUES (?, ?)"
    insert_game_FEN = "INSERT INTO game_FEN (game_id, FEN_id, move_number) VALUES (?, ?, ?)"
    try:
        cursor = connection.cursor()
        fens = {}
        next_fin_id = 0
        game = chess.pgn.read_game(pgn)
        while game is not None:
            game_id = game.headers["Site"]
            print(game_id)
            cursor.execute(insert_game, [game_id, game.headers["White"], game.headers["Black"], game.headers["Result"]])
            connection.commit()
            board = game.board()

            move_count = 0
            for move in game.mainline_moves():
                move_count += 1
                board.push(move)
                fen = board.fen()

                if fen not in fens:
                    next_fin_id += 1
                    fens[fen] = next_fin_id
                    fen_id = next_fin_id
                    print(fen_id)
                    cursor.execute(insert_FEN, [fen_id, fen])
                    connection.commit()
                else:
                    fen_id = fens[fen]

                cursor.execute(insert_game_FEN, [game_id, fen_id, move_count])
                connection.commit()

            game = chess.pgn.read_game(pgn)
    finally:
        connection.close()


def create_sqlite_db():
    if not os.path.isfile("chess.db"):
        connection = sqlite3.connect("chess.db")
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE Game (id TEXT PRIMARY KEY, pgn TEXT, white TEXT, black TEXT, result TEXT)''')
        cursor.execute('''CREATE TABLE FEN (id INTEGER PRIMARY KEY, FEN TEXT, evaluation REAL)''')
        cursor.execute('''CREATE TABLE Game_FEN (game_id TEXT, FEN_id INTEGER, move_number INTEGER, PRIMARY KEY(game_id, FEN_id, move_number))''')


def get_chess_dot_com_user():
    response = chessdotcom.get_player_profile("wombathammer")
    print(response.player)

def get_player_games():
    x = chessdotcom.get_player_games_by_month_pgn("wombathammer", "2021", "03")
    print(x)

get_player_games()
