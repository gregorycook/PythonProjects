
import lichess.api
from lichess.format import SINGLE_PGN

user = lichess.api.user("gcook1729")

print(user)

pgn = lichess.api.user_games('gcook1729', max=5000, format=SINGLE_PGN)
with open('gcook.pgn', 'w') as f:
    f.write(pgn)
