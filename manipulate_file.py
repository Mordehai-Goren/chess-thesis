import file_util as U
import basic_file_data as bf
from os import listdir
import stockfish_util as S
import game_2_features as F
import reporter as R

def moveResult2End(game):
    with open(game, 'r') as r:
        with open(game + "_", 'w') as w:
            first = True
            for l in r:
                if first and l[0] not in ['1-0', '0-1', '1/2-1/2']:
                    print ('First term not game result')
                    break 
                if not first:
                    w.write("\n")
                first = False
                l = l.split()
                
                
                l = l[1:-1] + [l[0]]
                l = ' '.join(l)
                
                if (l):
                    w.write(l)

def hasCastleMove(game):
    print ('Check Castling in %s'%game)
    with open(game, 'r') as r:
        for l in r:
            if 'O-O' in l:
                print (l)
                break
        else:
            print ("No casteling found")

def convertCasteling(game):
    print ('Convert castling to king move %s'%game)
    count = 0
    with open(game, 'r') as r:
        first = True
        with open(game + "_", 'w') as w:
            
            for l in r:
                if first:
                    first = False
                else:
                    w.write("\n")
                
                l = l.split()
                white = True
                newG = []
                for m in l:
                    if m.startswith('O-O-O'):
                        count+=1
                        if count < 30:
                            print (m)
                        if white:
                            m = m.replace('O-O-O','Kc1')
                        else:
                            m = m.replace('O-O-O','Kc8')
                        if count < 30:
                            print (m)
                    elif m.startswith('O-O'):
                        count+=1
                        if count < 30:
                            print (m)
                        if white:
                            m = m.replace('O-O','Kg1')
                        else:
                            m = m.replace('O-O','Kg8')
                        if count < 30:
                            print (m)
                    newG.append(m)
                    white = not white
                w.write(' '.join(newG))

def removeUnClearResults(game):
    print ("Removing un-clear results %s"%game)
    with open(game, 'r') as r:
        with open(game + "_", 'w') as w:
            with open(game + "_unclear", 'w') as wUnClear:
                for l in r:
                    ll = l.strip()
                    if ll.endswith('1-0') or ll.endswith('0-1') or ll.endswith('1/2-1/2'):
                        w.write(l)
                    else:
                        wUnClear.write(l)

def aggScoreFiles(game):
#     game = U.RAW_GAME_FOLDER + game
    scoreGame = U.toScoreF(game)
    game2scores = {}
    mark = {}
    
    doubles = 0
    
    for fName in listdir(U.RAW_GAME_FOLDER):
        fName = str(fName)
        if game.replace('.pgn','') not in fName:
            continue
        if 'score' not in fName:
            continue
        print (fName)
        with open(U.RAW_GAME_FOLDER + fName, 'r') as f:
            for l in f:
                l = l.split()
                key = ''
                full = ''
                for i in range(len(l)):
                    if not i % 2:
                        key += l[i] + " "
                    full += l[i] + " "
                key = key.strip()
                if key in game2scores:
                    doubles += 1
                game2scores[key] = full
                mark[key] = 1
                
                
    scoredGames = len(game2scores)
    print (scoredGames)
    print (doubles)
    count = 0
    with open(U.RAW_GAME_FOLDER + scoreGame + "_missing", 'w') as missing:
        with open(U.RAW_GAME_FOLDER + scoreGame + "_", 'w') as w:
            with open(U.RAW_GAME_FOLDER + game, 'r') as f:
                for l in f:
                    l = l.strip()
                    if l.endswith('1/2-1/2'):
                        continue
                    count += 1
                    if l in game2scores:
                        w.write(game2scores[l] + "\n")
                        mark[key] = 0
                    
                    if l not in game2scores:
                        missing.write(l + "\n")
                        print (l)
                        print (count)
                    if (count > scoredGames):
                        break
    
    for key in mark.keys():
        if mark[key]==0:
            print (key)
                

def createBalancedCorrectMistakeFile(gameInput):
    correctMore = 0
    with open(gameInput.replace('.txt', '_balanced.txt'), 'w') as w:
        with open(gameInput, 'r') as f:
            for l in f:
                dbID, correct, fen, san, nextSan, uci, nextUci = l.split('|')
                
                if (correct=="True"):
                    if correctMore >= 1:
                        continue
                    correctMore += 1
                else:
                    correctMore -= 1
            
                w.write(l)

def extractBalancedFen(gameInput):
    correctMore = 0
    with open(gameInput.replace('.txt', '_fen.txt'), 'w') as w:
        with open(gameInput, 'r') as f:
            for l in f:
                dbID, correct, fen, san, nextSan, uci, nextUci = l.split('|')
                
                if (correct=="True"):
                    if correctMore >= 1:
                        continue
                    correctMore += 1
                else:
                    correctMore -= 1
                
                w.write(correct)
                w.write('|')
                w.write(fen)
                w.write("\n")

def createBestMovePerDepth(gameInput):
    if '.txt' not in gameInput:
        print ("Wrong file: %s"%gameInput)
    with open(gameInput.replace('.txt', '_balanced_with_best.txt'), 'w') as w:
        with open(gameInput.replace('.txt', '_balanced.txt'), 'r') as f:
            for l in f:
                dbID, correct, fen, san, nextSan, uci, nextUci = l.split('|')
                bestMoves = S.getBestMovePerDepth(fen)
                bestMoves = '|'.join(bestMoves)
                l = l.strip()
                l += "|" + bestMoves
                w.write(l + "\n")
                

def compareFileAndBinary(binFile, textFile):
    data = F.loadFeatureFile(binFile)
    for entry in data:
        print (entry)
        break
    
    with open(textFile, 'r') as f:
        for l in f:
            print (l)
            break
    
def lichess2sanNNextFen():
    with open(U.LICHESS_RAW, 'r') as f:
        with open(U.LICHESS_SAN, 'w') as w:
            for l in f:
                PuzzleId,FEN,Moves,Rating,RatingDeviation,Popularity,NbPlays,Themes,GameUrl = l.split(',')
                fen, san = S.fenAndUci2SecondFenAndSan(FEN, Moves.split())
                w.write(PuzzleId + "," + Rating + "," + fen + "," + ' '.join(san) + "," + Themes + "\n")

def lichessTags():
    dd = {}
    with open(U.LICHESS_RAW, 'r') as f:
        for l in f:
            PuzzleId,FEN,Moves,Rating,RatingDeviation,Popularity,NbPlays,Themes,GameUrl = l.split(',')
            
            if Themes in dd:
                dd[Themes] += 1
            else:
                dd[Themes] = 1
                
            tags = Themes.split()
            for tag in tags:
                if tag in dd:
                    dd[tag] += 1
                else:
                    dd[tag] = 1
    for k, v in dd.items():
        print ('%s,%s'%(k, v))

def evenOdd2Result(filename):
    outcome = {'1-0':[0,0], '0-1':[0,0], '1/2-1/2':[0,0]}
    print (filename)
    sum = 0
    with open(filename, 'r') as r:
        for l in r:
            l = l.split()
            even = len(l) % 2
            result = l[-1]
            outcome[result][even] += 1
            sum += 1
    print (outcome)
    R.report('Source,Length,White,Black,Draw')
    R.report("%s,odd,%s,%s,%s"%(filename,outcome['1-0'][1]/sum,outcome['0-1'][1]/sum,outcome['1/2-1/2'][1]/sum))
    R.report("%s,even,%s,%s,%s"%(filename,outcome['1-0'][0]/sum,outcome['0-1'][0]/sum,outcome['1/2-1/2'][0]/sum))
                                 
            

if __name__=='__main__':
    if True:
        evenOdd2Result(U.PGN_MENTOR_RAW)
        evenOdd2Result(U.FICS_RAW)
    
    
    if False:
        lichessTags()
    
    if False:
        lichess2sanNNextFen()
    
#     extractBalancedFen(U.MISTAKE_RAW)
    if False:
        convertCasteling(U.PGN_MENTOR_RAW)
    
#     compareFileAndBinary(U.CHESS_DB, U.OLD_CHESS_DB_FEATURES)
#     aggScoreFiles(U.WALL)
#     createBalancedCorrectMistakeFile(U.MISTAKE_RAW)
#     createBestMovePerDepth(U.MISTAKE_RAW)
#     moveResult2End(U.FICS_RAW)
#     bf.extract_file_data(U.FICS_RAW + "_")
#     
#     moveResult2End(U.FICS_STRONG_RAW)
#     bf.extract_file_data(U.FICS_STRONG_RAW + "_")
    
#     hasCastleMove(U.CHESS_DB_RAW)
#     hasCastleMove(U.FICS_RAW)
#     hasCastleMove(U.FICS_STRONG_RAW)
#     hasCastleMove(U.WALL_RAW)

    
#     convertCasteling(U.CHESS_DB_RAW)
#     convertCasteling(U.WALL_RAW)
    
#     moveResult2End(U.FICS_STRONG)

#     removeUnClearResults(U.CHESS_DB_RAW)
#     removeUnClearResults(U.FICS_RAW)
#     removeUnClearResults(U.FICS_STRONG_RAW)
#     removeUnClearResults(U.WALL_RAW)
    
    