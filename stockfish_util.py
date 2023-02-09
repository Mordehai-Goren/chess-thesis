from pystockfish import *
import chess
from stockfish import Stockfish


# shalow = Engine(depth = 7, param = {'multiPV':2})
# deep = Engine(depth = 14, param = {'multiPV':2})

MATE_SCORE = 10000

def fixCasteling(m, board):
    if m.startswith('Kg1') and ' w ' in board.fen() and 'K' in board.fen().split(' w ')[1]:
        return m.replace('Kg1', 'O-O')
    if m.startswith('Kc1') and ' w ' in board.fen() and 'Q' in board.fen().split(' w ')[1]:
        return m.replace('Kc1', 'O-O-O')
    if m.startswith('Kg8') and ' b ' in board.fen() and 'k' in board.fen().split(' b ')[1]:
        return m.replace('Kg8', 'O-O')
    if m.startswith('Kc8') and ' b ' in board.fen() and 'q' in board.fen().split(' b ')[1]:
        return m.replace('Kc8', 'O-O-O')
    return m

engine = None

def getFenScore(fen):
    global engine
    if not engine:
        engine = Engine(depth = 10)
    engine.set_fen_position(fen)
    
    return getScore(engine)
    

def getFenFromMoves(moves):
    board = chess.Board()
    for m in moves:
        m = fixCasteling(m, board)
        board.push_san(m)
    return board.fen()

def getLastScoreAndFen(moves):
    global engine
    if not engine:
        engine = Engine(depth = 10)
    board = chess.Board()
    uci = []
    for m in moves:
        m = fixCasteling(m, board)
        m1 = board.push_san(m)
        uci.append(str(m1))
        
    engine.setposition(uci)
        
    if m.endswith('#'):
        score = MATE_SCORE 
    else:
        score = (getScore(engine))
            
    return score, board.fen()

def getScorePerMove(moves):
    global engine
    if not engine:
        engine = Engine(depth = 10)
    board = chess.Board()
    uci = []
    toRet = ''
    white = True
    for m in moves:
        toRet += m + " "
        m = fixCasteling(m, board)
        
        m1 = board.push_san(m)
#         print (m, m1)
        uci.append(str(m1))
#         print (moves)
        engine.setposition(uci)
        
        if m.endswith('#'):
            score = MATE_SCORE 
        else:
            score = (getScore(engine))
            
        if white:
            score = -score
            
        toRet += "%s "%score
        
        white = not white
    
    return toRet
        
def getScore(engine):
    engine.go()
    last_line = secondLastLine = ''
    while True:
        text = engine.stdout.readline().strip()
        split_text = text.split(' ')
        if split_text[0] == 'bestmove':
            if len(split_text)>=3:
                ponder=split_text[3]
            else:
                ponder=None
            
#             print (last_line)
            scoreCP = last_line.split(' score cp ')
            if len(scoreCP)==2:
                return int(scoreCP[1].split(' ')[0])
            scoreMate = last_line.split(' score mate ')
            if (scoreMate[1][0]=='-'):
                return -MATE_SCORE
            else:
                return MATE_SCORE
            
            return {'move': split_text[1],
                'ponder': ponder,
                'info': last_line,
                'add':secondLastLine,
                'text':text
                
                }
        secondLastLine = last_line
        last_line = text
        
def getBestMoves(shalow):
    shalow.go()
    last_line = secondLastLine = ''
    while True:
        text = shalow.stdout.readline().strip()
        split_text = text.split(' ')
        if split_text[0] == 'bestmove':
            if len(split_text)>=3:
                ponder=split_text[3]
            else:
                ponder=None
            return {'move': split_text[1],
            'ponder': ponder,
            'info': last_line,
            'add':secondLastLine,
            'text':text
            
            }
        secondLastLine = last_line
        last_line = text

def getBestMovePerDepth(fen, maxDepth = 10):
    global engine
    bestMoves = []
    for depth in range(0, maxDepth):
        if not engine:
            engine = Stockfish('C:\\dev\\tools\\workspace\\fics\\data_manipulation\\stockfish_8_x64.exe')
        engine.set_depth(depth+1)
        engine.set_fen_position(fen)
        bestMoves.append(engine.get_best_move())
#     print (bestMoves)
    return bestMoves

piece2feature = {}
def loadPiece2Feature():
    board = chess.Board()
    i = 0
    for p in str(board).replace('\n','').replace(' ',''):
        if p not in piece2feature:
            array = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            array[i] = 1
            piece2feature[p] = array
            i+=1 
loadPiece2Feature()

def board2Feature(board):
    feature = []
    for p in str(board):
        if p in piece2feature:
            feature+=piece2feature[p]
    return feature

def fen2Feature(fen):
    board = chess.Board(fen)
    return board2Feature(board)
    
#     features = board2Feature(board)
#     if ' b ' in fen:
#         features.append(0)
#     else:
#         features.append(1)
#     return features
    

def moves2Feature(moves):
    board = chess.Board()
    for m in moves:
        try:
            board.push_san(m)
        except:
            if m[0]=='K' and m[1]=='g':
                board.push_san("O-O")
            elif m[0]=='K' and m[1]=='c':
                board.push_san("O-O-O")
            else:
                raise
    return board2Feature(board)
#     features = board2Feature(board)
#     features.append(len(moves)%2)
#     return features

def fenAndUci2SecondFenAndSan(fen, uci):
    board = chess.Board(fen)
    san = board.variation_san([chess.Move.from_uci(m) for m in uci]).split()
    san = [m for m in san if not m.endswith('.')]
    san[0] = san[0].split('.')[-1]
    board.push_uci(uci[0])
    return board.fen(),san

def numberMoves(moves, start, white):
    s = '%s. '%start
    start += 1
    if not white:
        s += '... '
    
    for m in moves:
        if white:
            s += '%s. '%start
            start += 1
        s += m + ' '
        white = not white
    return s
    
    
    
if __name__=='__main__':
    
    if True:
        fen = 'r3kbnr/ppp2ppp/2n1pq2/3p1b2/3P4/1PPBPP2/P5PP/RNBQK1NR b KQkq - 2 6'
        print (numberMoves(fenAndUci2SecondFenAndSan(fen, 'f5d3 d1d3 h7h5 e1f1'.split())[1], 6, False))
        print (numberMoves(fenAndUci2SecondFenAndSan(fen, 'f6g5 d3f5 e6f5 e1f1'.split())[1], 6, False))
        
        print (numberMoves(fenAndUci2SecondFenAndSan(fen, 'f6g6 g1e2 g6g2 h1f1 f5g6 e2f4 g2h2 d1e2 h2e2 e1e2 g8f6 b1d2 f8d6 f4g6 h7g6 c1b2 e8c8 f1h1'.split())[1], 6, False))
        print (numberMoves(fenAndUci2SecondFenAndSan(fen, 'f5d3 d1d3 f6g6 d3g6 h7g6 c1a3 g6g5 e1f2 g8f6 a3f8 e8f8 g1e2 g5g4 b1d2 g4f3 g2f3 a7a5'.split())[1], 6, False))
    
    if False:
        engine = Stockfish('C:\\dev\\tools\\workspace\\fics\\data_manipulation\\stockfish_8_x64.exe', parameters={'MultiPV': 2})
        fen = 'r3kbnr/ppp2ppp/2n1pq2/3p1b2/3P4/1PPBPP2/P5PP/RNBQK1NR b KQkq - 2 6'
        engine.set_depth(4)
#         engine.set_pv(2)
#         engine._set_option({'MultiPV': 2})
        engine.set_fen_position(fen)
        print (getBestMoves(engine))
#         print (engine.get_parameters())
#         print (dir(engine))
#         Engine(depth = 7, param = {'multiPV':2})
        
        
    
    if False:
        print (getBestMovePerDepth('r3kbnr/ppp2ppp/2n1pq2/3p1b2/3P4/1PPBPP2/P5PP/RNBQK1NR b KQkq - 2 6'))
    
    if False:
        print (fen2Feature('2r3k1/p1q2pp1/Q3p2p/b1Np4/2nP1P2/4P1P1/5K1P/2B1N3 b - - 3 33'))
    
    if False:
        fen, san = fenAndUci2SecondFenAndSan('2r3k1/p1q2pp1/Q3p2p/b1Np4/2nP1P2/4P1P1/5K1P/2B1N3 b - - 3 33', 'c7b6 a6c8 g8h7 c8b7'.split())
        fen, san = fenAndUci2SecondFenAndSan('r3kb1r/pppqpn1p/5p2/3p1bpQ/2PP4/4P1B1/PP3PPP/RN2KB1R w KQkq - 1 11', 'b1c3 f5g4 h5g4 d7g4'.split())
    
#     print (fen2Feature('r1b1k2r/ppb2ppp/2N2n2/4q3/4P3/2N2P2/PP2B1PP/R1BQK2R b KQkq - 0 11'))
#     
#     print (moves2Feature('e4 e6 d4 d5 Nd2 Nf6 e5 Nfd7 f4 c5 c3 Nc6 Ndf3 cxd4 cxd4 f6 Bd3 Bb4+ Bd2 Qb6 Ne2 fxe5 fxe5 Kg8 a3 Be7 Qc2 Rxf3 gxf3 Nxd4 Nxd4 Qxd4 Kc1 Nxe5 Bxh7+ Kh8 Kb1 Qh4 Bc3 Bf6 f4 Nc4 Bxf6 Qxf6 Bd3 b5 Qe2 Bd7 Rhg1 Be8 Rde1 Bf7 Rg3 Rc8 Reg1 Nd6 Rxg7 Nf5 R7g5 Rc7 Bxf5 exf5 Rh5+'.split()))
#     print (fen2Feature('7k/p1r2b2/5q2/1p1p1p1R/5P2/P7/1P2Q2P/1K4R1 b - - 1 32'))
    
    
#     board = chess.Board()
#     print (str(board).replace('\n','').replace(' ',''))
#     board = chess.Board('r1b1k2r/ppb2ppp/2N2n2/4q3/4P3/2N2P2/PP2B1PP/R1BQK2R b KQkq - 0 11')
#     print (''.join(str(board).split()))

#     print(str(board))
#     engine = Engine(depth = 10)
#     engine = Stockfish('C:\\dev\\tools\\workspace\\fics\\data_manipulation\\stockfish_8_x64.exe')
#     engine.set_depth(1)
# 
#     engine.set_fen_position("rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")
#     print (engine.get_best_move())
# #     print (getBestMoves(engine))
#     pass
#     createScoresFile(F.WALL_RAW)
#     createScoresFile(F.FICS_RAW)
#     createScoresFile(F.CHESS_DB_RAW)
#     createScoresFile(F.FICS_STRONG_RAW)