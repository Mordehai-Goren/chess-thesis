import game_2_features as F
import file_util as U
import classifier as C
import metrics as M
import numpy as np
from stockfish_util import MATE_SCORE
import stockfish_util as S
from sklearn.ensemble import RandomForestClassifier
import reporter as R
import random
import time
from time import sleep

MIN_SIZE = 100
MAX_SIZE = 5000

def checkBalanced(countW, outcome):
    if outcome==F.DRAW:
        return countW, False
    
    if outcome==F.WHITE_WIN:
        if countW > 0:
            return countW, False
        countW += 1
    
    if outcome==F.BLACK_WIN:
        if countW < -0:
            return countW, False
        countW -= 1
        
    return countW, True

def collectPerLength(data, moves2Use, lastX = None, allMoves = True, balanced = True, maxScore = False, minSize = MIN_SIZE, maxSize = MAX_SIZE):
    xTrain = []; yTrain = []; countTrain = 0
    xTest = []; yTest = []; countTest = 0
    countExtra = 0
    
    countW = 0
    
    np.random.shuffle(data)
    
    featuresPerMove = F.FEATURES_PER_MOVE
    if maxScore:
        featuresPerMove += 1
    
    if not lastX:
        lastX = moves2Use
    
    for entry in data:
        x = entry[1:]
        movesInEntry = len(x) / featuresPerMove
        
        if moves2Use > movesInEntry:
            continue
        
        if allMoves and moves2Use < movesInEntry:
            continue
        
        y = entry[0]
        
        if balanced:
            countW, proceed = checkBalanced(countW, y)
            if not proceed:
#                 print (countW)
                continue
        
        
#         x = x[ (moves2Use - lastX) * featuresPerMove : moves2Use * featuresPerMove]
        
#         print (moves2Use, lastX)
#         print (x)
#         xx = x[ (moves2Use - lastX) * featuresPerMove : moves2Use * featuresPerMove - featuresPerMove]
#         x = x[ (moves2Use - lastX) * featuresPerMove : moves2Use * featuresPerMove]
        x = x[ (moves2Use - lastX) * featuresPerMove : moves2Use * featuresPerMove]
        
        #Skip high scores
        if maxScore:
            if x[-1] > maxScore or x[-1]<-maxScore:
                continue
        
        if countTest < minSize:
            xTest.append(x); yTest.append(y); countTest += 1
            continue
        
        if countTrain < maxSize:
            xTrain.append(x); yTrain.append(y); countTrain += 1
            continue
        
        countExtra += 1
        
    classes = len(set(yTest))
    if classes<2 or set(yTrain)!=set(yTest):
        return [], [], 0, [],[], 0, 0, 0
        
    xTrain = np.array(xTrain); yTrain = np.array(yTrain)
    xTest = np.array(xTest); yTest = np.array(yTest)
        
    return xTrain, yTrain, countTrain, xTest, yTest, countTest, classes, countExtra

def iterateLength(featureFile, lastX = None, allMoves = True, balanced = True, maxScore = False, minSize = MIN_SIZE, maxSize = MAX_SIZE, specificLength = None, modolu = 1, models = None):
    summary = "file: %s; lastX: %s; allMoves: %s; balanced: %s; maxScore: %s; minSize: %s; maxSize: %s\n"%(featureFile, lastX, allMoves, balanced, maxScore, minSize, maxSize)
    
    print ("Start %s"%summary)
    
    data = F.loadFeatureFile(featureFile)
    
    accPerLength = {};tookPerLength ={}
    
    if not models:
        models = ['svm', 'rf', 'nb', 'ann']
    
    print (models)
    
    for m in models:
        accPerLength[m] = {};tookPerLength[m] = {};
        
    countPerLength = {}; 
    countTrainAll = 0; countTestAll = 0
    
    for gameLength in range(11, 101):
        if specificLength and gameLength!=specificLength:
            continue
        
        if gameLength % modolu:
            continue
        
        print (gameLength)
        
        R.setLabel('%s^%s^'%(featureFile, gameLength))
        
        xTrain, yTrain, countTrain, xTest, yTest, countTest, classes, extra = \
            collectPerLength(data, gameLength, lastX=lastX, allMoves=allMoves, balanced=balanced, maxScore = maxScore, minSize=minSize, maxSize=maxSize)
        
        
        if classes==1:
            print ("Skipping Length %s only %s classes"%(gameLength, classes))
            continue
        
        if (countTrain < MIN_SIZE):
            print ("Skipping Length %s only %s games"%(gameLength, (countTest + countTrain)))
            continue
        
#         print ("Length %s. %s for train %s for test"%(gameLength, countTrain, countTest))
        
        classes = 2 if balanced else 3 
        
#         countPerLength[gameLength] = countTrain + countTest
        countPerLength[gameLength] = countTrain + countTest + extra
        
        countTrainAll += countTrain
        countTestAll += countTest
        
        
        tookPerLength, accPerLength = M.saveMetricsPerFramework(xTrain, yTrain, xTest, yTest, tookPerLength, accPerLength, gameLength, classes)
#         print (gameLength, countTrain, countTest, countTrain + countTest + extra,accPerLength['rf'][gameLength])
        
        
    R.report("Test^%s^Train^%s"%(countTestAll, countTrainAll))
    print ("Test: %s. Train: %s"%(countTestAll, countTrainAll))
    summary += "Test: %s. Train: %s\n"%(countTestAll, countTrainAll)
    
    summary += M.summarizerPerFramework(countPerLength, tookPerLength, accPerLength)
    print ("Done %s"%featureFile)
    return summary

def classifyFullLengh(featureFile, maxSize = MAX_SIZE, models = None):
    return iterateLength(featureFile, lastX = None, allMoves = True, balanced = False, maxSize = maxSize, models=models)

def classifyOngoing(featureFile, maxSize = MAX_SIZE, specificLength = None, modolu = 1, models = None):
    return iterateLength(featureFile, lastX = None, allMoves = False, balanced = True, maxSize = maxSize, specificLength = specificLength, modolu = modolu, models=models)
    
def classifyOngoingLastX(featureFile, lastX, maxSize = MAX_SIZE, specificLength = None, modolu = 1, models = None):
    return iterateLength(featureFile, lastX = lastX, allMoves = False, balanced = True, maxSize=maxSize, specificLength = specificLength, modolu = modolu, models=models)

def classifyOngoingLastXWithScore(featureFile, lastX, maxSize = MAX_SIZE, maxScore = MATE_SCORE, models = None):
    return iterateLength(U.toScoreF(featureFile), lastX = lastX, allMoves = False, balanced = True, maxSize=maxSize, maxScore = maxScore, models=models)

def classifyFullLenghWithScore(featureFile, maxSize = MAX_SIZE, maxScore = MATE_SCORE, models = None):
    return iterateLength(U.toScoreF(featureFile), lastX = None, allMoves = True, balanced = True, maxSize=maxSize, maxScore = maxScore, models=models)


def classifyByLength(featureFile, startMove = 10, lastMove = 100, maxGames = 200000):
    allGames = 0
    correct = 0
    count = 0
    with open(U.RAW_GAME_FOLDER + featureFile, 'r') as f:
        for l in f:
            count += 1
            if count > maxGames:
                break
            l = l.split()
            outcome = l[-1]
            
 
#             print (l)
            
            l = l[:-1]
            if len(l)<startMove or len(l) > lastMove:
                continue
            

            
            allGames += 1
            guess = '1-0' if len(l) % 2 else '0-1'
            
#             print (outcome)
#             print (l)
#             print (len(l))
#             print (guess)
            
            if guess == outcome:
#                 print ('correct')
                correct += 1
            else:
                print (outcome)
#             print ("-------------")
    print (featureFile)
    print (correct)
    print (allGames)
    print (correct/allGames)
            

def classifyByScore(featureFile, startMove = 10, lastMove = 100, maxScore = MATE_SCORE, balanced = True):
    allMoves = 0
    correctScores = 0
    
    countW = 0
    
    with open(U.RAW_GAME_FOLDER + U.toScoreF(featureFile), 'r') as f:
        
        for l in f:
            move = 0
            l = l.split()
            whiteWin = F.score2Code[l[-1]]
            
            if balanced:
                countW, proceed = checkBalanced(countW, whiteWin)
                if not proceed:
                    continue
            
            it = iter(l[startMove*2:-1])
            for _ in it:
                score = int(next(it))
                
                if score > maxScore or score < -maxScore:
                    continue
                
                allMoves += 1
                positiveScore = score > 0
                
                
                if whiteWin:
                    if positiveScore:
                        correctScores += 1
                else:
                    if not positiveScore:
                        correctScores += 1
                move += 1
                if move > lastMove:
                    break
#     outcome = "classifyByScore %s Start Move: %s. Correct: %s. Correct: %s. Moves: %s. Max Score: %s\n"%(U.toScoreF(featureFile), startMove, (correctScores / allMoves), correctScores, allMoves, maxScore)
    outcome = 'Accuracy^%s^Correct^%s^Moves^%s\n'%((correctScores / allMoves), correctScores, allMoves)
    R.report('Accuracy^%s^Correct^%s^Moves^%s\n'%((correctScores / allMoves), correctScores, allMoves)) 
    print (outcome)
    return outcome

def extractExtremeCases(featureFile, gameLength, minSize = 2000, maxSize = 100000):
    print ("Start %s"%featureFile)
#     data = F.loadFeatureFile(featureFile)

    data = F.getGame2Feature(featureFile, maxGames = 100000)
    gameMoves = []
    
    with open(U.RAW_GAME_FOLDER + featureFile, 'r') as f:
        for l in f:
            gameMoves.append(l)
    
    xTrain = []; yTrain = []; countTrain = 0
    xTest = []; yTest = []; countTest = 0
    testMoves = []
    countExtra = 0
    
    countW = 0
    
    for entry, moves in zip(data, gameMoves):
        x = entry[1:1+F.FEATURES_PER_MOVE*gameLength]
        movesInEntry = len(x) / F.FEATURES_PER_MOVE
        
        if gameLength > movesInEntry:
            continue
        
        y = entry[0]
        
        countW, proceed = checkBalanced(countW, y)
        if not proceed:
            continue
        
        if countTest < minSize:
            xTest.append(x); yTest.append(y); countTest += 1
            testMoves.append(moves.split()[:gameLength])
            continue
        
        if countTrain < maxSize:
            xTrain.append(x); yTrain.append(y); countTrain += 1
            continue
        
        countExtra += 1
        
    xTrain = np.array(xTrain); yTrain = np.array(yTrain)
    xTest = np.array(xTest); yTest = np.array(yTest)
    
    model = RandomForestClassifier(n_estimators=21)
    model.fit(xTrain, yTrain)
#     model = C.classify('rf', xTrain, yTrain)
    probabilities = model.predict_proba(xTest)
    predictions = model.predict(xTest)
    
    with open("scores_prop_%s"%featureFile, 'w') as w:
        for prob, p, x, y, moves in zip(probabilities, predictions, xTest, yTest, testMoves):
            if True or prob[0]==0 or prob[0]==1:
                print (prob)
                print (p)
                
    #             print (F.features2Moves(x))
                
    #             print (x)
                print (y)
    #             print (moves)
                print (' '.join(moves))
                
                
    #             fen = S.getFenFromMoves(moves)
    #             print (fen)
    #             print (S.getFenScore(fen))
    #             print (S.getScorePerMove(moves))
                
                score, fen  = S.getLastScoreAndFen(moves)
    
                print (fen)
                print (score)
                
                w.write('%s,'%fen)
                w.write('%s,'%prob[1])
                w.write('%s,'%y)
                w.write("%s\n"%score)
#             print (S.getLastScoreAndFen(moves))

def collectPositionPerLength(game, moves2Use, minSize = MIN_SIZE, maxSize = MAX_SIZE):
    xTrain = []; yTrain = []; countTrain = 0
    xTest = []; yTest = []; countTest = 0
    
    countExtra = 0
    countW = 0
    
    data = []
    with open(U.RAW_GAME_FOLDER + game, 'r') as r:
        for l in r:
            moves = l.split()
            y = F.score2Code[moves[-1]]
            
            if len(moves)<moves2Use+1:
                continue
            
            if y==F.DRAW:
                continue
            
            data.append(l)
    
    random.shuffle(data)


    for l in data:
#     with open(U.RAW_GAME_FOLDER + game, 'r') as r:
#         for l in r:
        moves = l.split()
        y = F.score2Code[moves[-1]]
            
#             if len(moves)<moves2Use+1:
#                 continue
#             
#             if y==F.DRAW:
#                 continue
            
        countW, proceed = checkBalanced(countW, y)
        if not proceed:
            continue
        
        moves = moves[:moves2Use]
        
        if countTest < minSize:
            x = S.moves2Feature(moves)
            xTest.append(x); yTest.append(y); countTest += 1
            continue
    
        if countTrain < maxSize:
            x = S.moves2Feature(moves)
            xTrain.append(x); yTrain.append(y); countTrain += 1
            continue
    
        countExtra += 1
        
    data = []
            
    classes = len(set(yTest))
    if classes<2 or set(yTrain)!=set(yTest):
        return [], [], 0, [],[], 0, 0, 0
        
    xTrain = np.array(xTrain); yTrain = np.array(yTrain)
    xTest = np.array(xTest); yTest = np.array(yTest)
        
    return xTrain, yTrain, countTrain, xTest, yTest, countTest, classes, countExtra

def classifyByPosition(game, minSize = 100, maxSize = 1000, modolu = 1, allIn1 = False):
    print ("Start %s"%game)
    
    accPerLength = {};tookPerLength ={}
#     accPerLength['stockfish'] = {};tookPerLength['stockfish'] = {};
    accPerLength['ann'] = {};tookPerLength['ann'] = {};
#     accPerLength['svm'] = {};tookPerLength['svm'] = {};
    accPerLength['rf'] = {};tookPerLength['rf'] = {};
    accPerLength['nb'] = {};tookPerLength['nb'] = {};
    
    countPerLength = {}; 
    countTrainAll = 0; countTestAll = 0
    
    start_time = time.time()
    for gameLength in range(11, 101):
        if gameLength % modolu:
            continue
         
        print (gameLength)
        
        if allIn1:
            xTrain, yTrain, countTrain, xTest, yTest, countTest, classes, extra = \
                collectPosition(game, gameLength, minSize=minSize, maxSize=maxSize)
                
                
            if False:
                took = time.time() - start_time
                print (len(xTrain))
                print (len(xTest))
                print ("Took", took)
                sleep(1000)
                return
            
        else:
            xTrain, yTrain, countTrain, xTest, yTest, countTest, classes, extra = \
                collectPositionPerLength(game, gameLength, minSize=minSize, maxSize=maxSize)
        
        
        if classes==1:
            print ("Skipping Length %s only %s classes"%(gameLength, classes))
            continue
        
        if (countTrain < MIN_SIZE):
            print ("Skipping Length %s only %s games"%(gameLength, (countTest + countTrain)))
            continue
        
        
#         countPerLength[gameLength] = countTrain + countTest
        countPerLength[gameLength] = countTrain + countTest + extra
        
        countTrainAll += countTrain
        countTestAll += countTest
        
        print ("gameLength: %s; countTrain: %s; countTest: %s"%(gameLength, countTrain, countTest))
        
        
        tookPerLength, accPerLength = M.saveMetricsPerFramework(xTrain, yTrain, xTest, yTest, tookPerLength, accPerLength, gameLength, classes)
        
        print (tookPerLength['ann'][gameLength])
#         print (tookPerLength['svm'][gameLength])
#         
        print (accPerLength['ann'][gameLength])
        
        if allIn1:
            break
        
#         print (accPerLength['svm'][gameLength])
        
#         print (gameLength, countTrain, countTest, countTrain + countTest + extra,accPerLength['rf'][gameLength])
        
        
    R.report("Test^%s^Train^%s"%(countTestAll, countTrainAll))
    print ("Test: %s. Train: %s"%(countTestAll, countTrainAll))
#     summary += "Test: %s. Train: %s\n"%(countTestAll, countTrainAll)
    
    M.summarizerPerFramework(countPerLength, tookPerLength, accPerLength)
#     summary += M.summarizerPerFramework(countPerLength, tookPerLength, accPerLength)
    print ("Done %s"%game)
#     return summary

def collectPosition(game, minMoves = 10, maxMoves = 100, minSize = MIN_SIZE, maxSize = MAX_SIZE):
    xTrain = []; yTrain = []; countTrain = 0
    xTest = []; yTest = []; countTest = 0
    
    countExtra = 0
    countW = 0
    
    data = []
    with open(U.RAW_GAME_FOLDER + game, 'r') as r:
        for l in r:
            moves = l.split()
            y = F.score2Code[moves[-1]]
            
            if len(moves)<minMoves+1:
                continue
            
            if y==F.DRAW:
                continue
            
            data.append(l)
    
    random.shuffle(data)


    for l in data:
#     with open(U.RAW_GAME_FOLDER + game, 'r') as r:
#         for l in r:
        origmoves = l.split()
        y = F.score2Code[origmoves[-1]]
            
#             if len(moves)<moves2Use+1:
#                 continue
#             
#             if y==F.DRAW:
#                 continue
            
        countW, proceed = checkBalanced(countW, y)
        if not proceed:
            continue
        
        for moves2Use in range(minMoves, min(maxMoves, len(origmoves)-1)):
            moves = origmoves[:moves2Use]
            
            if countTest < minSize:
                x = S.moves2Feature(moves)
                xTest.append(x); yTest.append(y); countTest += 1
                continue
        
            if countTrain < maxSize:
                x = S.moves2Feature(moves)
                xTrain.append(x); yTrain.append(y); countTrain += 1
                continue
    
        countExtra += 1
        
    data = []
    
    classes = len(set(yTest))
    if classes<2 or set(yTrain)!=set(yTest):
        return [], [], 0, [],[], 0, 0, 0
        
    xTrain = np.array(xTrain); yTrain = np.array(yTrain)
    xTest = np.array(xTest); yTest = np.array(yTest)
        
    return xTrain, yTrain, countTrain, xTest, yTest, countTest, classes, countExtra

def collectLastXNoBuckets(data, lastX = 10, minSize = 10000, maxSize = 100000, minMove = 10, maxMove = 100, fullGame = False):
    xTrain = []; yTrain = []; countTrain = 0
    xTest = []; yTest = []; countTest = 0
    countExtra = 0
    
    countW = 0
    
    np.random.shuffle(data)
    
    printit = 0
    
    featuresPerMove = F.FEATURES_PER_MOVE
    
    for entry in data:
        
        if fullGame and maxMove*featuresPerMove+1<len(entry):
            continue
        
        if fullGame and lastX*featuresPerMove+1>len(entry):
            continue
        
        orig = entry[1:maxMove*featuresPerMove]
        
        movesInEntry = len(orig) / featuresPerMove
        
        y = entry[0]
        countW, proceed = checkBalanced(countW, y)
        if not proceed:
            continue
        
        if fullGame:
            x = entry[-lastX*featuresPerMove:]
            
            if printit:
                print (x)
                print (orig)
                print (len(x))
                printit -= 1
        
            if countTest < minSize:
                xTest.append(x); yTest.append(y); countTest += 1
                continue
            
            if countTrain < maxSize:
                xTrain.append(x); yTrain.append(y); countTrain += 1
                continue
        
        else:
            for firstMove in range(int(movesInEntry)-minMove+1):
                x = orig[ firstMove * featuresPerMove : (firstMove + lastX) * featuresPerMove]
            
                if printit:
                    print (x)
            
                if countTest < minSize:
                    xTest.append(x); yTest.append(y); countTest += 1
                    continue
                
                if countTrain < maxSize:
                    xTrain.append(x); yTrain.append(y); countTrain += 1
                    continue
        
        if printit:
            print (orig)
            printit -= 1
        
        countExtra += 1
    
    xTrain = np.array(xTrain); yTrain = np.array(yTrain)
    xTest = np.array(xTest); yTest = np.array(yTest)
    
    print (xTrain)
    print (yTrain)
    print (xTest)
    print (yTest)
        
    return xTrain, yTrain, countTrain, xTest, yTest, countTest, 2, countExtra
    
   
def classifyLastXNoBuckets(game, lastX, minSize = 10000, maxSize = 100000, maxMove = 100, fullGame = False):
    print ("Start %s"%game)
    
    accPerLength = {};tookPerLength ={}
#     accPerLength['ann'] = {};tookPerLength['ann'] = {};
#     accPerLength['svm'] = {};tookPerLength['svm'] = {};
    accPerLength['rf'] = {};tookPerLength['rf'] = {};
#     accPerLength['nb'] = {};tookPerLength['nb'] = {};
    
    countPerLength = {}; 
    countTrainAll = 0; countTestAll = 0
    
    gameLength = 1
    
    data = F.loadFeatureFile(game)
    
    xTrain, yTrain, countTrain, xTest, yTest, countTest, classes, extra = \
        collectLastXNoBuckets(data, lastX, minSize=minSize, maxSize=maxSize, maxMove = maxMove, fullGame = fullGame)
    
    countPerLength[gameLength] = countTrain + countTest + extra
    
    countTrainAll += countTrain
    countTestAll += countTest
    
    print ("gameLength: %s; countTrain: %s; countTest: %s"%(gameLength, countTrain, countTest))
    
    tookPerLength, accPerLength = M.saveMetricsPerFramework(xTrain, yTrain, xTest, yTest, tookPerLength, accPerLength, gameLength, classes)
    
        
    R.report("Test^%s^Train^%s"%(countTestAll, countTrainAll))
    print ("Test: %s. Train: %s"%(countTestAll, countTrainAll))
#     summary += "Test: %s. Train: %s\n"%(countTestAll, countTrainAll)
    
    M.summarizerPerFramework(countPerLength, tookPerLength, accPerLength)
#     summary += M.summarizerPerFramework(countPerLength, tookPerLength, accPerLength)
    print ("Done %s"%game) 

def classifyLastXRangeBuckets(game, lastX, minSize = 10000, maxSize = 100000, bucket = 10):
    print ("Start %s"%game)
    
    accPerLength = {};tookPerLength ={}
#     accPerLength['ann'] = {};tookPerLength['ann'] = {};
#     accPerLength['svm'] = {};tookPerLength['svm'] = {};
#     accPerLength['rf'] = {};tookPerLength['rf'] = {};
    accPerLength['nb'] = {};tookPerLength['nb'] = {};
    
    countPerLength = {}; 
    countTrainAll = 0; countTestAll = 0
    
    gameLength = 1
    
    data = F.loadFeatureFile(game)
    
    for gameLength in range(1, int(100/bucket)+1):
        
        minMove = gameLength*bucket
        maxMove = gameLength*bucket+bucket
        
        xTrain, yTrain, countTrain, xTest, yTest, countTest, classes, extra = \
            collectLastXNoBuckets(data, lastX, minSize=minSize, maxSize=maxSize, minMove = minMove, maxMove = maxMove)
            
            
        #         countPerLength[gameLength] = countTrain + countTest
        countPerLength[gameLength] = countTrain + countTest + extra
        
        countTrainAll += countTrain
        countTestAll += countTest
        
        print ("gameLength: %s; countTrain: %s; countTest: %s; minMove: %s; maxMove: %s"%(gameLength, countTrain, countTest, minMove, maxMove))
        tookPerLength, accPerLength = M.saveMetricsPerFramework(xTrain, yTrain, xTest, yTest, tookPerLength, accPerLength, gameLength, classes)
        
        print (accPerLength['nb'][gameLength])
        
        
    print ("gameLength: %s; countTrain: %s; countTest: %s"%(gameLength, countTrain, countTest))
    
    tookPerLength, accPerLength = M.saveMetricsPerFramework(xTrain, yTrain, xTest, yTest, tookPerLength, accPerLength, gameLength, classes)
    
        
    R.report("Test^%s^Train^%s"%(countTestAll, countTrainAll))
    print ("Test: %s. Train: %s"%(countTestAll, countTrainAll))
#     summary += "Test: %s. Train: %s\n"%(countTestAll, countTrainAll)
    
    M.summarizerPerFramework(countPerLength, tookPerLength, accPerLength)
#     summary += M.summarizerPerFramework(countPerLength, tookPerLength, accPerLength)
    print ("Done %s"%game) 

n2c = {}
for i,c in enumerate('abcdefgh'):
    n2c[i+1]=c 
    
#UCI
def feature2Move(feature):
    moves = ''
#     for increment in (0, 10, 20, 30, 40, 50, 60, 70, 80, 90):
    for increment in (0, 10, 20, 30):
        for i, piece in enumerate('RNBQKP'):
            if feature[increment+i]:
                break
        capture = 'x' if feature[increment+6] else ''
        check = '+' if feature[increment+7] else ''
        col = n2c[feature[increment+8]]
#         col = str(feature[increment+8])
        row = str(feature[increment+9])
        moves += piece + capture + col + row + check + "^"
    return moves

if __name__=='__main__':
    
    if False:
        for dataset in [U.FICS, U.PGN_MENTOR]:
            R.setLabel("classifyOngoing^%s^%s^"%(dataset, 1000 * 90))
            classifyOngoing(dataset, maxSize=1000, models = ['rnn'])
            R.setLabel("classifyOngoing^%s^%s^"%(dataset, 2000 * 90))
            classifyOngoing(dataset, maxSize=2000, models = ['rnn'])
            R.setLabel("classifyOngoing^%s^%s^"%(dataset, 4000 * 90))
            classifyOngoing(dataset, maxSize=4000, models = ['rnn'])
    
        
    if False:
        for dataset in [U.FICS, U.PGN_MENTOR]:
            R.setLabel("ClassifyPositionsAllIn1^%s^"%dataset)
            classifyByPosition(dataset, minSize = 10000, maxSize = 100000, allIn1 = True)
    
    if False:
        for dataset in [U.FICS, U.PGN_MENTOR]:
            R.setLabel("ClassifyPositions^%s^"%dataset)
            classifyByPosition(dataset, minSize = 100, maxSize = 1000)
            
            
    if False:
        for dataset in [U.FICS, U.PGN_MENTOR]:
            R.setLabel("classifyLastXNoBuckets4000000^%s^%s^"%(10, dataset))
            classifyLastXNoBuckets(dataset, lastX = 10, maxSize=40000, maxMove = 60, fullGame = True)   
    
    if True:
        for dataset in [U.FICS, U.PGN_MENTOR]:
            R.setLabel("classifyLastXNoBuckets4000000^%s^%s^"%(4, dataset))
            classifyLastXNoBuckets(dataset, lastX = 4, maxSize=4000000, minSize=40000)
    
    if False:
        for dataset in [U.FICS, U.PGN_MENTOR]:
            for lastX in range(1,11):
#                 R.setLabel("classifyLastXNoBuckets1000000^%s^%s^"%(lastX, dataset))
#                 classifyLastXNoBuckets(dataset, lastX = lastX, maxSize=1000000)
#                 R.setLabel("classifyLastXNoBuckets2000000^%s^%s^"%(lastX, dataset))
#                 classifyLastXNoBuckets(dataset, lastX = lastX, maxSize=2000000)
                R.setLabel("classifyLastXNoBuckets4000000^%s^%s^"%(lastX, dataset))
                classifyLastXNoBuckets(dataset, lastX = lastX, maxSize=4000000)
#                 R.setLabel("classifyLastXNoBuckets8000000^%s^%s^"%(lastX, dataset))
#                 classifyLastXNoBuckets(dataset, lastX = lastX, maxSize=8000000)
    
    if False:
        for dataset in [U.FICS, U.PGN_MENTOR]:
            R.setLabel("classifyOngoing^%s^%s^"%(dataset, 1000 * 90))
            classifyOngoing(dataset, maxSize=1000)
            R.setLabel("classifyOngoing^%s^%s^"%(dataset, 2000 * 90))
            classifyOngoing(dataset, maxSize=2000)
            R.setLabel("classifyOngoing^%s^%s^"%(dataset, 4000 * 90))
            classifyOngoing(dataset, maxSize=4000)
    
    if False:
        for dataset in [U.FICS, U.PGN_MENTOR]:
            for lastX in [1,5,10]:
                R.setLabel("classifyOngoingLastX^%s^%s^"%(dataset, lastX))
                classifyOngoingLastX(dataset, lastX = lastX, maxSize=50000, models = ['rf'])
            R.setLabel("classifyOngoing^%s^"%(dataset))
            classifyOngoing(dataset, maxSize=50000, models = ['rf'])
            
    if False:
        for dataset in [U.FICS, U.PGN_MENTOR]:
            for lastX in range(1,11):
                R.setLabel("classifyOngoingLastX^%s^%s^"%(dataset, lastX))
                classifyOngoingLastX(dataset, lastX = lastX, maxSize=50000, models = ['nb'])
            R.setLabel("classifyOngoing^%s^"%(dataset))
            classifyOngoing(dataset, maxSize=50000, models = ['nb'])
    
    if False:
        for dataset in [U.FICS, U.PGN_MENTOR]:
            
            if False:
                lastX = 5
                classifyLastXRangeBuckets(dataset, lastX = lastX, maxSize=300000, bucket = 90)
            
            if False: 
                for bucket in [10,20,30]:
                    R.setLabel("classifyLastXRangeBuckets^%s^%s^%s^"%(lastX,bucket, dataset))
                    classifyLastXRangeBuckets(dataset, lastX = lastX, maxSize=300000, bucket = bucket)
            
            if False:
                for lastX in range(1,11):
                    R.setLabel("classifyLastXNoBuckets^%s^%s^"%(lastX, dataset))
                    classifyLastXNoBuckets(dataset, lastX = lastX, maxSize=100000)
    
    if False:
        for dataset in [U.FICS, U.PGN_MENTOR]:
            classifyOngoingLastX(dataset, lastX = 10, maxSize=10000, modolu = 10)
    
    if False:
        for dataset in [U.FICS, U.PGN_MENTOR]:
            classifyOngoing(dataset, maxSize=100000, models = ['rf'])
    
    if False:
        for dataset in [U.FICS, U.PGN_MENTOR]:
            classifyOngoing(dataset, maxSize=100000)

    
    if False:
        for dataset in [U.FICS, U.PGN_MENTOR]:
            classifyOngoing(dataset, maxSize=100000)
            for lastX in range(1, 11):
                R.setLabel("classifyOngoingLastX_%s^%s^"%(lastX, dataset))
                classifyOngoingLastX(dataset, lastX = lastX, maxSize=100000)
    
    if False:
        summary = "\n\n***********\n"
        for dataset in [U.FICS, U.PGN_MENTOR]:
#             R.setLabel("classifyFullLengh^%s^"%dataset)
#             summary += classifyFullLengh(dataset)
            
#             R.setLabel("classifyByScore^%s^"%dataset)
#             summary += classifyByScore(dataset, startMove = 10, lastMove = 90)
                
            R.setLabel("classifyOngoingModolu10^%s^"%dataset)
            summary += classifyOngoing(dataset, maxSize=10000, modolu = 10)
            for lastX in range(1, 11):
                R.setLabel("classifyOngoingLastX_%s^%s^"%(lastX, dataset))
                summary += classifyOngoingLastX(dataset, lastX = lastX, maxSize=10000, modolu = 10)
            
#             R.setLabel("Position_Move 50^%s^"%(dataset))
#             summary += M.classifyAsIs(dataset.replace(".pgn", "_50.fen"))
#             R.setLabel("LastX_5_Move 50^%s^"%(dataset))
#             summary += classifyOngoingLastX(dataset, lastX = 5, maxSize=100000, specificLength=50)
#             R.setLabel("classifyByScore_Move 50^%s^"%(dataset))
#             summary += classifyByScore(dataset, startMove = 50, lastMove = 0)
        print (summary)   
         
    if False:
        for dataset in [U.FICS, U.PGN_MENTOR]:
            R.setLabel("ClassifyPositionsModolu10^%s^"%dataset)
            classifyByPosition(dataset, minSize = 1000, maxSize = 10000, modolu = 10)        
        
    
    if False:
        for dataset in [U.FICS, U.CHESS_DB, U.FICS_STRONG, U.WALL]:
            extractExtremeCases(dataset, 50)
#     summary = '\n\n============================\n\n'
# #     for dataset in [U.FICS, U.CHESS_DB]:

    if False:
        summary = "\n\n***********\n"
        for dataset in [U.FICS, U.CHESS_DB, U.FICS_STRONG, U.WALL, U.PGN_MENTOR]:
     
            summary += "\n"
            summary += dataset
            summary += "\n***********\n"
            summary += classifyByScore(dataset, startMove = 50, lastMove = 0)
            summary += M.classifyAsIs(dataset.replace(".pgn", "_50.fen"))
            summary += classifyOngoingLastX(dataset, lastX = 5, maxSize=1000000, specificLength = 50)
            
            summary += classifyFullLengh(dataset)
            summary += classifyOngoing(dataset)
            summary += classifyOngoingLastX(dataset, lastX = 1)
            summary += classifyOngoingLastX(dataset, lastX = 5)
            summary += classifyOngoingLastX(dataset, lastX = 10)
            
#         summary += classifyOngoingLastX(dataset, 10, specificLength = 50, maxSize = 1000000)
#         summary += M.classifyAsIs(dataset.replace(".pgn", "_50.fen.pgn"))
#         summary += M.classifyAsIs(dataset.replace(".pgn", "_50.fen.pgn5"))
#         summary += classifyOngoingLastX(dataset, 10, maxSize=3000) 
#         for lastX in range(1, 11):
#             summary += classifyOngoingLastXWithScore(dataset, lastX=lastX, maxScore = MATE_SCORE, maxSize=40000)
#             summary += classifyOngoingLastXWithScore(dataset, lastX=lastX, maxScore = 25, maxSize=40000)
#             summary += classifyByScore(dataset, maxScore = MATE_SCORE)
#             summary += classifyByScore(dataset, maxScore = 25)
#             summary += classifyOngoingLastX(dataset, lastX, maxSize=40000)
#             summary += classifyOngoingLastX(dataset, lastX, maxSize=40000)
#             summary += classifyOngoingLastX(dataset, lastX, maxSize=40000)
        
#     print (summary)
    
    if False:
        summary = ''
        summary = "\n\n*****************\n"
        for dataset in [U.FICS, U.CHESS_DB, U.FICS_STRONG, U.WALL]:
            summary += classifyOngoingLastX(dataset, 10, maxSize=2000)
        
        summary += "\n------------------------\n"
        summary += "11 estimators"
        summary += "\n------------------------\n"
        C.RF_ESTIMATORS = 11
        for dataset in [U.FICS, U.CHESS_DB, U.FICS_STRONG, U.WALL]:
            summary += classifyOngoingLastX(dataset, 10, maxSize=2000)
        print (summary)
            
    '''
    for dataset in [U.FICS, U.CHESS_DB, U.FICS_STRONG, U.WALL]:
        summary += "Dataset: %s\n"%dataset
        summary += classifyFullLengh(dataset) 
        summary += classifyOngoing(dataset, maxSize=2000)
        summary += classifyOngoingLastX(dataset, 10, maxSize=2000)
        summary += classifyOngoingLastX(dataset, 10, maxSize=5000)
        summary += classifyOngoingLastX(dataset, 5, maxSize=2000)
        summary += classifyOngoingLastX(dataset, 5, maxSize=5000) 
        summary += classifyByScore(dataset, maxScore = MATE_SCORE)
        summary += classifyByScore(dataset, maxScore = 25)
        summary += classifyOngoingLastXWithScore(dataset, lastX = 10, maxScore = 25)
        summary += classifyOngoingLastXWithScore(dataset, lastX = 5, maxScore = 25)
        summary += classifyOngoingLastXWithScore(dataset, lastX = 1, maxScore = 25)
        summary += "-------------------------------\n"
        print ("-------------------------------")
    
    print (summary)
#     for dataset in [U.FICS, U.CHESS_DB, U.FICS_STRONG, U.WALL]:
#     for dataset in [U.CHESS_DB, U.WALL]:
#     for dataset in [U.WALL]:
#         classifyByLength(dataset)
        
        
#     for dataset in [U.FICS]:
    for dataset in [U.FICS_STRONG]:
#     for dataset in [U.FICS, U.CHESS_DB, U.FICS_STRONG, U.WALL]:
        summary += classifyByScore(dataset, maxScore = 0)
        summary += classifyByScore(dataset, maxScore = 5)
        summary += classifyByScore(dataset, maxScore = 10)
#         summary += classifyOngoingLastXWithScore(dataset, lastX = 10, maxSize = 2000)
#         summary += classifyOngoingLastXWithScore(dataset, lastX = 5, maxSize = 5000, maxScore = 25)
#         summary += classifyOngoingLastXWithScore(dataset, lastX = 3, maxSize = 5000, maxScore = 25)
#         summary += classifyOngoingLastXWithScore(dataset, lastX = 1, maxSize = 5000, maxScore = 20)
#         summary += classifyOngoingLastXWithScore(dataset, lastX = 1, maxSize = 5000, maxScore = 0)
    
    print (summary)
    '''
            
            