import file_util as U
import numpy as np
from copy import copy
import stockfish_util as S
from time import time, sleep

FEATURES_PER_MOVE = 10

pawn =   [0,0,0,0,0,1]
d = {'R':[1,0,0,0,0,0],
     'N':[0,1,0,0,0,0],
     'B':[0,0,1,0,0,0],
     'Q':[0,0,0,1,0,0],
     'K':[0,0,0,0,1,0],
     'a':pawn, 'b':pawn, 'c':pawn, 'd':pawn, 'e':pawn, 'f':pawn, 'g':pawn, 'h':pawn, 
     }

dd = {}
for i,c in enumerate('abcdefgh'):
    dd[c]=i+1
    dd['%s'%(i+1)]=i+1

def moveFeatures(m):
    l = copy(d[m[0]])
    l.append(1 if 'x' in m else 0)
    l.append(1 if (m.endswith('+') or m.endswith('#')) else 0)

    if m[-1] in dd:
        l.append(dd[m[-2]])
        l.append(dd[m[-1]])
    elif m[-2] in dd:
        l.append(dd[m[-3]])
        l.append(dd[m[-2]])
    elif m[-3] in dd:
        l.append(dd[m[-4]])
        l.append(dd[m[-3]])
    else:
        l.append(dd[m[-5]])
        l.append(dd[m[-4]])
    return l

WHITE_WIN = 1
BLACK_WIN = 0
DRAW = 2
score2Code = {'1-0':WHITE_WIN, '0-1':BLACK_WIN, '1/2-1/2':DRAW}

def gameNScores2Feature(game):
    print ('Converting %s score to features'%game)
    count = 0
    data = []
    with open(U.RAW_GAME_FOLDER + game.replace('.pgn', '_score.pgn'), 'r') as r:
        for l in r:
            try:
                l = l.split()
                score = l[-1]
                
                features = [score2Code[score]]
                
                it = iter(l[0:-1])
                for m in it:
                    features+=moveFeatures(m)
                    features+=[int(next(it))]#The score
                
                features = np.array(features)
                data.append(features)
                count += 1
                
            except Exception as e:
                print (l)
                raise e
            
    data = np.array(data)
    np.save(U.FEATURES_GAME_FOLDER + game.replace('.pgn', '_score.pgn'), data)

def getGame2Feature(game, maxGames = 200000):
    print ('Converting %s to features'%game)
    count = 0
    data = []
#     sumMoves = 0
    with open(U.RAW_GAME_FOLDER + game, 'r') as r:
        for l in r:
            try:
                l = l.split()
                score = l[-1]
                
#                 sumMoves += len(l)-1
                
                features = [score2Code[score]]
                for m in l[0:-1]:
                    features+=moveFeatures(m)
                features = np.array(features)
                data.append(features)
                count += 1
                if count > maxGames:
                    break
            except Exception as e:
                print (l)
                raise e
            
#     data = np.array(data)
#     print (sumMoves)
    return data
    
def game2Feature(game, maxGames = 200000):
    data = getGame2Feature(game, maxGames = maxGames)
    np.save(U.FEATURES_GAME_FOLDER + game, data)

def loadScoreFeatureFile(game):
    return loadFeatureFile(game.replace('.pgn', '_score.pgn'))
    
def loadFeatureFile(game):
    return np.load(U.FEATURES_GAME_FOLDER + game + ".npy", allow_pickle=True)

def saveMistakeFeature(game):
    correctCount = 0
    count = 0
    data = []
    with open(U.RAW_GAME_FOLDER + game, 'r') as r:
        for l in r:
            dbID, correct, fen, san, nextSan, uci, nextUci = l.split('|')
            correct = 1 if correct=='True' else 0
            
            before = san.split()[-5:]
            after = nextSan.split()[:5]
            
            if len(before)!=5 or len(after)!=5:
                continue
            
            if correct and correctCount > -1:
                continue
            
            if correct:
                correctCount += 1
            else:
                correctCount -= 1
                
            count+=1
            
            if count < 30:
                print (san)
                print (nextSan)
            
            hasCasteling = [b for b in before if 'O' in b]
            hasCasteling = hasCasteling if hasCasteling else [a for a in after if 'O' in a]
            
            if hasCasteling:
                san = san.split()
                nextSan = nextSan.split()
                
                newSan = []
                newNextSan =[]
            
                castleRow = 1
                for m in san:
                    if m.startswith('O-O-O'):
                        m = 'Kc%s%s'%(castleRow, ('+' if m.endswith('+') else ''))
                    elif m.startswith('O-O'):
                        m = 'Kg%s%s'%(castleRow, ('+' if m.endswith('+') else ''))
                    castleRow = 8 if castleRow==1 else 1
                    newSan.append(m)
                
                for m in nextSan:
                    if m.startswith('O-O-O'):
                        m = 'Kc%s%s'%(castleRow, ('+' if m.endswith('+') else ''))
                    elif m.startswith('O-O'):
                        m = 'Kg%s%s'%(castleRow, ('+' if m.endswith('+') else ''))
                    castleRow = 8 if castleRow==1 else 1
                    newNextSan.append(m)
            
                before = newSan[-5:]
                after = newNextSan[:5]
                
            features = [correct]
            
            for m in before:
                features+=moveFeatures(m)
            for m in after:
                features+=moveFeatures(m)
            
            if count < 30:
                print (before)
                print (after)
                print (features)    
            
            data.append(features)
    print (count, correctCount)
    np.save(U.FEATURES_GAME_FOLDER + game, data)

def saveFen2Features(game):
    data = []
    with open(U.RAW_GAME_FOLDER + game, 'r') as r:
        for l in r:
            correct, fen = l.split('|')
            
            correct = 1 if correct=='True' else 0
            features = [correct]
            
            feature = S.fen2Feature(fen)
            features += feature
            
            data.append(features)
    np.save(U.FEATURES_GAME_FOLDER + game, data)

def saveXmovesAsFenFeature(game, numMoves, addMoveFeature = False, lastX = ''):
    data = []
    if '.pgn' not in game:
        print ("Mistake in file: %s"%game)
        return
    
    print ("saveXmovesAsFenFeature %s. Num moves: %s"%(game, numMoves))
    count = 0
    
    whiteWin = 0
    with open(U.RAW_GAME_FOLDER + game, 'r') as r:
        for l in r:
            moves = l.split()
            outcome = score2Code[moves[-1]]
            
            if len(moves)<numMoves+1:
                continue
            
            if outcome==DRAW:
                continue
            
            if outcome==WHITE_WIN:
                if whiteWin > 5:
                    continue
                whiteWin+=1
            else:
                whiteWin-=1
                
            count += 1
            
            moves = moves[:numMoves]
            
            features = [outcome]
            features += S.moves2Feature(moves)
            
            if lastX:
                moves = moves[-lastX:]
            
            if addMoveFeature:
                for m in moves:
                    features+=moveFeatures(m)
                
            features = np.array(features)
            
            data.append(features)
            
            if not count % 1000:
                print (count)
            
            if count >= 100000:
                break
    
    print (count)
    return data
    np.save(U.FEATURES_GAME_FOLDER + game.replace('.pgn', '_%s.fen%s%s'%(numMoves, ('.pgn' if addMoveFeature else ''), lastX)), data)

def moveFeatures(m):
    l = copy(d[m[0]])
    l.append(1 if 'x' in m else 0)
    l.append(1 if (m.endswith('+') or m.endswith('#')) else 0)

    if m[-1] in dd:
        l.append(dd[m[-2]])
        l.append(dd[m[-1]])
    elif m[-2] in dd:
        l.append(dd[m[-3]])
        l.append(dd[m[-2]])
    elif m[-3] in dd:
        l.append(dd[m[-4]])
        l.append(dd[m[-3]])
    else:
        l.append(dd[m[-5]])
        l.append(dd[m[-4]])
    return l

def features2Moves(features):
    moves = []
    print (len(features))
    for i in range(int(len(features)/FEATURES_PER_MOVE)):
        index = i*FEATURES_PER_MOVE
        
        piece = ''
        if features[index]:
            piece='R'
        elif features[index+1]:
            piece='N'
        elif features[index+2]:
            piece='B'
        elif features[index+3]:
            piece='Q'
        elif features[index+4]:
            piece='K'
        index+=6
            
        capture = 'x' if features[index] else ''
        index+=1
        check = '+' if features[index] else ''
        index+=1
        
        m = piece + capture + chr(ord('a')+features[index]-1) + '%s'%features[index+1] + check
        moves.append(m)
    return moves

def liChess2MoveFeatures():
    print ('Converting LICHESS to features')
    data = []
    
    countChecks = 0
    with open(U.LICHESS_SAN, 'r') as f:
        for l in f:
            puzId, rating, fen, san, themes = l.strip().split(',')
            features = [themes, int(rating)]
            
            white = 'w' not in fen
            
            for m in san.split():
                if m.startswith('O'):
                    countChecks += 1
                    check = '+' if m.endswith('+') else ''
                    rank = '1' if white else '8'
                    
                    if m.startswith('O-O-O'):
                        m = 'Kc' + rank + check
                    else:
                        m = 'Kg' + rank + check
                    
                    if countChecks < 10:
                        print (san)
                        print (m)
                        
                
                features+=moveFeatures(m)
                white = not white
            data.append(features)
            
    np.save(U.FEATURES_GAME_FOLDER + U.LICHESS, data)
    
    
def liChess2PositionFeatures():
    print ('Converting LICHESS to position features')
    data = []
    
    count = 0
    
    with open(U.LICHESS_SAN, 'r') as f:
        for l in f:
            puzId, rating, fen, san, themes = l.strip().split(',')
            
            features = [themes, int(rating)]
            features += S.fen2Feature(fen)
            
            data.append(features)
            count += 1
            
            if count < 10:
                print (features)
            
            if count >= 20000:
                break
            
    np.save(U.FEATURES_GAME_FOLDER + U.LICHESS + '.fen', data)
    

if __name__=='__main__':
    
    if True:
    #     data = loadFeatureFile('pgnmentor_50.fen')
        data = loadFeatureFile('pgnmentor.pgn')
        print (len(data))
        count = 0
        sumMoves = 0
        for l in data:
            count += 1
            sumMoves -= 1
            sumMoves += len(l)
    #         print (l)
            if count < 100:
                print (len(l))
    #             break
        print (sumMoves)
    
    if False:
        start_time = time()
        data = saveXmovesAsFenFeature(U.FICS, numMoves = 1)
        took = time() - start_time
        print ("Took", took)
        sleep(1000)
    
    if False:
        start_time = time()
        data = getGame2Feature(U.FICS, maxGames = 100000)
        took = time() - start_time
        print ("Took", took)
        sleep(1000)
    
    if False:
        liChess2PositionFeatures()
        data = loadFeatureFile('lichess_db_puzzle.csv.fen')
        print (data[0])
        
    if False:
        liChess2MoveFeatures()
        data = loadFeatureFile('lichess_db_puzzle.csv')
        print (data[0])
#     loadFeatureFile(U.WALL.replace('.pgn', '_%s.fen'%50))
    
#     saveXmovesAsFenFeature(U.WALL, 50)
#     saveXmovesAsFenFeature(U.CHESS_DB, 50)
#     saveXmovesAsFenFeature(U.PGN_MENTOR, 50)
#     saveXmovesAsFenFeature(U.FICS_STRONG, 50)
#     saveXmovesAsFenFeature(U.FICS, 50)

#     saveXmovesAsFenFeature(U.WALL, 50, addMoveFeature = True, lastX = 5)
#     saveXmovesAsFenFeature(U.CHESS_DB, 50, addMoveFeature = True, lastX = 5)
#     saveXmovesAsFenFeature(U.PGN_MENTOR, 50, addMoveFeature = True, lastX = 5)    
#     saveXmovesAsFenFeature(U.FICS_STRONG, 50, addMoveFeature = True, lastX = 5)    
#     saveXmovesAsFenFeature(U.FICS, 50, addMoveFeature = True, lastX = 5)    
    
    
    
    
#     saveFen2Features(U.MISTAKE_FEN)
#     game2Feature(U.PGN_MENTOR)
#     loadFeatureFile(U.PGN_MENTOR)  

    
#     game2Feature(U.CHESS_DB)
#     loadFeatureFile(U.CHESS_DB)  
#     game2Feature(U.WALL)
#     loadFeatureFile(U.WALL)    
#     game2Feature(U.FICS)
#     loadFeatureFile(U.FICS)
#     game2Feature(U.FICS_STRONG)
#     loadFeatureFile(U.FICS_STRONG)
#     data = loadFeatureFile(U.FICS_STRONG)

    if False:
        gameNScores2Feature(U.WALL)
        data = loadScoreFeatureFile(U.WALL)    
    
#     gameNScores2Feature(U.FICS)
#     gameNScores2Feature(U.FICS_STRONG)
#     data = loadScoreFeatureFile(U.FICS)

#     gameNScores2Feature(U.CHESS_DB)
#     data = loadScoreFeatureFile(U.CHESS_DB)  
    
#     gameNScores2Feature(U.CHESS_DB)
#     data = loadScoreFeatureFile(U.CHESS_DB)  
#     saveMistakeFeature(U.MISTAKE)
