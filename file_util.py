ORIG_GAME_FOLDER = 'C:/dev/tools/workspace/fics/2018/'
RAW_GAME_FOLDER = 'C:/dev/tools/workspace/fics/datasets/raw/'
OUTPUT_GAME_FOLDER = 'C:/dev/tools/workspace/fics/datasets/outputs/'
MODEL_GAME_FOLDER = 'C:/dev/tools/workspace/fics/datasets/models/'
FEATURES_GAME_FOLDER = 'C:/dev/tools/workspace/fics/datasets/features/'

LOG_FOLDER = 'C:/dev/tools/workspace/fics/logs/'

CHESS_DB = 'many_games.pgn'
WALL = 'wall_2020.pgn'
FICS_STRONG = '2018_blitz_2000.pgn'
FICS = '2018_games.pgn'
PGN_MENTOR = 'pgnmentor.pgn'


CHESS_DB_RAW = RAW_GAME_FOLDER + CHESS_DB
WALL_RAW = RAW_GAME_FOLDER + WALL
FICS_STRONG_RAW = RAW_GAME_FOLDER + FICS_STRONG
FICS_RAW = RAW_GAME_FOLDER + FICS
PGN_MENTOR_RAW = RAW_GAME_FOLDER + PGN_MENTOR

WALL_RAW_SCORES = RAW_GAME_FOLDER + WALL.replace('.pgn', '_score.pgn')
FICS_RAW_SCORES = RAW_GAME_FOLDER + FICS.replace('.pgn', '_score.pgn')

CHESS_DB_FEATURES = FEATURES_GAME_FOLDER + CHESS_DB
WALL_FEATURES = FEATURES_GAME_FOLDER + WALL
FICS_STRONG_FEATURES = FEATURES_GAME_FOLDER + FICS_STRONG
FICS_FEATURES = FEATURES_GAME_FOLDER + FICS
PGN_MENTOR_FEATURES = FEATURES_GAME_FOLDER + PGN_MENTOR

OLD_CHESS_DB_FEATURES = 'C:/dev/tools/workspace/fics/2018/many_games.pgn_features'

def toScoreF(game):
    return game.replace('.pgn', '_score.pgn')


MISTAKE = 'one_move_mistake.txt'
MISTAKE_RAW = RAW_GAME_FOLDER + MISTAKE
MISTAKE_FEATURES = FEATURES_GAME_FOLDER + MISTAKE

MISTAKE_FEN = 'one_move_mistake_fen.txt'
MISTAKE_FEN_RAW = RAW_GAME_FOLDER + MISTAKE_FEN
MISTAKE_FEN_FEATURES = FEATURES_GAME_FOLDER + MISTAKE_FEN

LICHESS = 'lichess_db_puzzle.csv'
LICHESS_RAW = RAW_GAME_FOLDER + LICHESS
LICHESS_SAN = RAW_GAME_FOLDER + LICHESS.replace('.csv','.fen_pgn')
