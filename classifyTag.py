import game_2_features as F
import file_util as U
import classifier as C
import metrics as M
import numpy as np
from stockfish_util import MATE_SCORE
import stockfish_util as S
from sklearn.ensemble import RandomForestClassifier
from joblib import dump, load
import reporter as R
import time

# import time

MIN_SIZE = 100
MAX_SIZE = 5000


def getMoveByDepth():
    count = 0
    d = {}
    with open(U.LICHESS_SAN, 'r') as f:
            for l in f:
                puzId, rating, fen, san, themes = l.strip().split(',')
                d[puzId] = S.getBestMovePerDepth(fen)
#                 w.write(puzId + ",")
#                 w.write(','.join(S.getBestMovePerDepth(fen)))
#                 w.write("\n")
                count += 1
                if count >= 2000:
                    break
    count = 0
    with open(U.LICHESS_RAW, 'r') as f:
        with open(U.LICHESS_SAN + ".depth", 'w') as w:
            for l in f:
                PuzzleId,FEN,Moves,Rating,RatingDeviation,Popularity,NbPlays,Themes,GameUrl = l.split(',')
                if PuzzleId in d:
                    moves = d[PuzzleId]
                    count += 1
                    
                    w.write(PuzzleId + ",")
                    w.write(','.join(moves))
                    w.write("," + Moves.split()[1])
                    w.write("," + Rating)
                    w.write("\n")
                    
                    if count >= 2000:
                        break
                
                
                

def classifyTagByPos(tag, minSize = 1000, maxSize = 200000, frameworks = ['nb', 'rf', 'ann'] ):
    checkrating = tag=='rating'
    
    xTrain = []; yTrain = []; countTrain = 0
    xTest = []; yTest = []; countTest = 0
    
    more = 0
    count = 0
    
    start_time = time.time()
    
    print (tag)
    
        #can also use LICHESS_RAW with a different split...
    with open(U.LICHESS_SAN, 'r') as f:
        for l in f:
            puzId, rating, fen, san, themes = l.strip().split(',')
            
            if checkrating:
                y = int(rating) > 1500
            else:
                y = tag in themes
                
            if y:
                if more > 0:
                    continue
                more += 1
            else:
                if more < 0:
                    continue
                more -= 1
            
            if not rating and tag not in themes:
                continue
            
            x = S.fen2Feature(fen)
            
            if countTest < minSize:
                xTest.append(x); yTest.append(y); countTest += 1
                continue
        
            if countTrain < maxSize:
                xTrain.append(x); yTrain.append(y); countTrain += 1
                continue
            
            break
    
    print ("Test: %s. Train: %s"%(countTest, countTrain))
    took = time.time() - start_time
    R.setLabel("lichess_position^%s^%s^prepare^%s^"%(tag,countTrain,took))
    M.summarizerPerFrameworkAllOn1(frameworks, xTrain, yTrain, xTest, yTest)

def classifyTag(tag, moves2Use = 6, minSize = 1000, maxSize = 200000, byMove = True, frameworks = ['nb', 'rf', 'ann'] ):
    print ("Start %s by %s"%(tag, 'move' if byMove else 'position'))
    data = F.loadFeatureFile(U.LICHESS + ('' if byMove else '.fen'))
    
    rating = tag=='rating'
    
    accPerLength = {};tookPerLength ={}
    accPerLength['ann'] = {};tookPerLength['ann'] = {};
#     accPerLength['svm'] = {};tookPerLength['svm'] = {};
    accPerLength['rf'] = {};tookPerLength['rf'] = {};
    accPerLength['nb'] = {};tookPerLength['nb'] = {};
    
    xTrain = []; yTrain = []; countTrain = 0
    xTest = []; yTest = []; countTest = 0
    
    countTag = 0
    
    np.random.shuffle(data)
    
    featuresPerMove = F.FEATURES_PER_MOVE
    
    count = 0
    
    more = 0
    
    for entry in data:
        
        if rating:
            if byMove:
                y = entry[1] > 1500
            else:
                y = int(entry[1]) > 1500
        else:
            y = tag in entry[0]
        
        if y:
            if more > 0:
                continue
            more += 1
        else:
            if more < 0:
                continue
            more -= 1
            
        count += 1
        
        x = entry[2:]
        if byMove:
            movesInEntry = len(x) / featuresPerMove
            
            if moves2Use > movesInEntry:
                continue
            
            x = x [ : moves2Use * featuresPerMove]
        else:
            x = x.astype(int)
            
        if countTest < minSize:
            xTest.append(x); yTest.append(y); countTest += 1
            continue
        
        if countTrain < maxSize:
            xTrain.append(x); yTrain.append(y); countTrain += 1
            continue
        
    xTrain = np.array(xTrain); yTrain = np.array(yTrain)
    xTest = np.array(xTest); yTest = np.array(yTest)
    
    R.setLabel("%s^%s^%s^%s^"%(tag,'moves' if byMove else 'position', moves2Use, countTrain))
    
    print ("Test: %s. Train: %s"%(countTest, countTrain))
    summary = "Test: %s. Train: %s\n"%(countTest, countTrain)
    
#     frameworks = ['rf']
#     
#     if byMove:
#         frameworks = ['nb', 'rf', 'ann'] 
#         
#     frameworks = ['nb', 'rf', 'ann']
#     frameworks = ['ann', 'rnn']
#     frameworks = ['nb', 'rf', 'ann', 'svm']
#     summary += "Before: %s; After: %s; \n"%(before, after)
    summary += M.summarizerPerFrameworkAllOn1(frameworks, xTrain, yTrain, xTest, yTest)
    print ("Done %s by %s"%(tag, 'move' if byMove else 'position'))
    return summary


def saveLichessModels(tag, moves2Use = 6, minSize = 1000, maxSize = 200000):
    print ("Start %s"%tag)
    data = F.loadFeatureFile(U.LICHESS)
    
    rating = tag.startswith('rating')
    if rating:
        minScore = (1500 if tag=='rating' else int(tag.replace('rating','')))
    
    xTrain = []; yTrain = []; countTrain = 0
    xTest = []; yTest = []; countTest = 0
    
    np.random.shuffle(data)
    featuresPerMove = F.FEATURES_PER_MOVE
    
    count = 0
    more = 0
    
    for entry in data:
        if rating:
            y = entry[1] > minScore
        else:
            y = tag in entry[0]
        
        if y:
            if more > 0:
                continue
            more += 1
        else:
            if more < 0:
                continue
            more -= 1
            
        count += 1
        
        x = entry[2:]
        
        movesInEntry = len(x) / featuresPerMove
        
        if moves2Use > movesInEntry:
            continue
        
        x = x [ : moves2Use * featuresPerMove]
            
        if countTest < minSize:
            xTest.append(x); yTest.append(y); countTest += 1
            continue
        
        if countTrain < maxSize:
            xTrain.append(x); yTrain.append(y); countTrain += 1
            continue
        
    xTrain = np.array(xTrain); yTrain = np.array(yTrain)
    xTest = np.array(xTest); yTest = np.array(yTest)
    
    model = RandomForestClassifier(n_estimators=100)
    model.fit(xTrain, yTrain)
    dump(model, U.MODEL_GAME_FOLDER + tag)
    print ("Done %s"%tag)

def checkLichessOnSavedModels(tag):
    fens = []
    movess = []
    themess = []
    features = []
    
    count = 0
    
    with open(U.LICHESS_SAN, 'r') as f:
        for l in f:
            puzId, rating, fen, san, themes = l.strip().split(',')
            
            moves = san.split()
            if len(moves)<6:
                continue
            moves = moves[0:6]
            
            hasCasteling = [m for m in moves if 'O' in m]
            
            if hasCasteling:
                continue #Never Mind...
            
            feature = []
            for m in moves:
                feature+=F.moveFeatures(m)
            feature = np.array(feature)
            features.append(feature)
            
            fens.append(fen)
            movess.append(san)
            themess.append(themes)
            
            count += 1
            if count > 100000:
                break
    
    features = np.array(features)
    model = load(U.MODEL_GAME_FOLDER + tag)
    probabilities = model.predict_proba(features)
    
    count = 0
    with open(U.OUTPUT_GAME_FOLDER + tag + '.dis' + ".csv", 'w') as w:
        for pro, fen, moves, themes in zip(probabilities, fens, movess, themess):
            
            if False:
                w.write("%s,%s,%s,%s,%s\n"%(tag in themes, fen, themes, moves, pro[1]))
                count+=1
            
            if True:
                if tag in themes:
                    if pro[1]<0.1:
                        count += 1
                        w.write("%s,%s,%s,%s\n"%(fen, themes, moves, pro[1]))
                else:
                    if pro[1]>0.9:
                        count += 1
                        w.write("%s,%s,%s,%s\n"%(fen, themes, moves, pro[1]))
    
            if count > 40000:
                break
            

    

def checkMistakeOnSavedModels(tag, onlyMistakes = True):
    count = 0
    features = []
    fens = []
    movess = []
    corrects = []
    
    with open(U.RAW_GAME_FOLDER + U.MISTAKE, 'r') as r:
        for l in r:
            dbID, correct, fen, san, nextSan, uci, nextUci = l.split('|')
            
            if onlyMistakes and correct=='True':
                continue #Too easy
            
            before = san.split()[-1:]
            after = nextSan.split()[:5]
            moves = before + after
            
            if len(moves)!=6:
                continue
            
            hasCasteling = [m for m in moves if 'O' in m]
            
            if hasCasteling:
                continue #Never Mind...
            
            fens.append(fen)
            movess.append(moves)
            corrects.append(correct)
            
            feature = []
            for m in moves:
                feature+=F.moveFeatures(m)
            feature = np.array(feature)
            features.append(feature)
            
            count += 1
            if count > 40000:
                break
                
    features = np.array(features)
    
    model = load(U.MODEL_GAME_FOLDER + tag)
    probabilities = model.predict_proba(features)
    
    with open(U.OUTPUT_GAME_FOLDER + tag + ".csv", 'w') as w:
        for pro, fen, moves, correct in zip(probabilities, fens, movess, corrects):
            if onlyMistakes:
                w.write("%s,%s,%s\n"%(fen, ' '.join(moves), pro[1]))
            else:
                w.write("%s,%s,%s,%s\n"%(correct, fen, ' '.join(moves), pro[1]))

def checkMistakeOnGivenMoves(moves, tag = None, model = None):
    if not model:
        model = load(U.MODEL_GAME_FOLDER + tag)
    features = []
    for m in moves:
        features+=F.moveFeatures(m)
    features = np.array(features)
    features = np.array([features])
    
    probabilities = model.predict_proba(features)
    predictions = model.predict(features)
    
    for pro, pre in zip(probabilities, predictions):
        return (pro, pre)

def exractDetails():
    tags = {}
    lengths = {}
    with open(U.LICHESS_RAW, 'r') as f:
        for l in f:
            PuzzleId,FEN,Moves,Rating,RatingDeviation,Popularity,NbPlays,Themes,GameUrl = l.split(',')
            l = len(Moves.split())
            if l in lengths:
                lengths[l]+=1
            else:
                lengths[l]=1
            for tag in Themes.split():
                if tag in tags:
                    tags[tag]+=1
                else:
                    tags[tag]=1
    
    for k,v in tags.items():
        print (k,v)
    
    for k,v in lengths.items():
        print (k,v)

def extractDiff(tag, moves2Use = 6, minSize = 1000, maxSize = 200000):
    print ("Start %s"%tag)
    data = F.loadFeatureFile(U.LICHESS)
    
    xTrain = []; yTrain = []; countTrain = 0
    
    np.random.shuffle(data)
    featuresPerMove = F.FEATURES_PER_MOVE
    
    count = 0
    more = 0
    
    for entry in data:
        y = tag in entry[0]
        
#         if y:
#             if more > 0:
#                 continue
#             more += 1
#         else:
#             if more < 0:
#                 continue
#             more -= 1
            
        count += 1
        
        x = entry[2:]
        
        movesInEntry = len(x) / featuresPerMove
        
        if moves2Use > movesInEntry:
            continue
        
        x = x [ : moves2Use * featuresPerMove]
            
        if countTrain < maxSize:
            xTrain.append(x); yTrain.append(y); countTrain += 1
            continue
        break
        
    xTrain = np.array(xTrain); yTrain = np.array(yTrain)
    
    model = RandomForestClassifier(n_estimators=100)
    model.fit(xTrain, yTrain)

#     fens = []
#     urls = []
    puzids = []
    movess = []
    themess = []
    features = []
    id2url = {}
    
    count = 0

    with open(U.LICHESS_SAN, 'r') as f:
        for l in f:
            puzId, rating, fen, san, themes = l.strip().split(',')
            
            moves = san.split()
            if len(moves)<6:
                continue
            moves = moves[0:6]
            
            hasCasteling = [m for m in moves if 'O' in m]
            
            if hasCasteling:
                continue #Never Mind...
            
            feature = []
            for m in moves:
                feature+=F.moveFeatures(m)
            feature = np.array(feature)
            features.append(feature)
            
            puzids.append(puzId)
#             fens.append(fen)
            movess.append(san)
            themess.append(themes)
            
            count += 1
            if count > 100000:
                break
    

    
    features = np.array(features)
    probabilities = model.predict_proba(features)
    
    agree10 = agree90 = range10_90 = disagree10 = disagree90 = 0
    for pro, themes in zip(probabilities, themess):
        included = tag in themes
        if pro[1]>=0.1 and pro[1]<=0.9:
            range10_90+=1
            continue
        if pro[1]<0.1:
            if included:
                disagree10+=1
            else:
                agree10+=1
            continue
        if pro[1]>0.9:
            if included:
                agree90+=1
            else:
                disagree90+=1
            continue
        
    R.report("%s,%s,%s,%s,%s,%s"%(tag, range10_90, agree10, agree90, disagree10, disagree90))
    
    if True:
        return
    
    with open(U.LICHESS_RAW, 'r') as f:
        for l in f:
            PuzzleId,FEN,Moves,Rating,RatingDeviation,Popularity,NbPlays,Themes,GameUrl = l.split(',')
            id2url[PuzzleId] = GameUrl.replace("\n","").replace("\t","")
    
    count1 = 20;count2=20;count3=20;count4=20
    countRandom = 20
    count = 0
    with open(U.OUTPUT_GAME_FOLDER + tag + '.dis' + ".csv", 'w') as w:
        w.write("url,id,prediction,actual,themse,moves,probability\n")
        for pro, puzId, moves, themes in zip(probabilities, puzids, movess, themess):
            
            if False:
                w.write("%s,%s,%s,%s,%s,%s\n"%(id2url[puzId],tag in themes, puzId, themes, moves, pro[1]))
                count+=1
            
            if True:
                included = tag in themes
                if included:
                    if pro[1]<0.1 and count1>0:
#                         count += 1
                        count1-=1
                        w.write("%s,%s,%s,%s,%s,%s,%s\n"%(id2url[puzId],puzId,pro[1]>0.5, included, themes, moves, pro[1]))
                else:
                    if pro[1]>0.9 and count2>0:
                        count += 1
                        count2-=1
                        w.write("%s,%s,%s,%s,%s,%s,%s\n"%(id2url[puzId],puzId,pro[1]>0.5, included, themes, moves, pro[1]))
                
                if pro[1]>0.1 and pro[1]<0.9:
                    if included and count3>0:
                        count3-=1
                        w.write("%s,%s,%s,%s,%s,%s,%s\n"%(id2url[puzId],puzId,pro[1]>0.5, included, themes, moves, pro[1]))
                    if not included and count4>0:
                        count4-=1
                        w.write("%s,%s,%s,%s,%s,%s,%s\n"%(id2url[puzId],puzId,pro[1]>0.5, included, themes, moves, pro[1]))
                    
            if count > 40000:
                break

if __name__=='__main__':
    
    if True:
        for tag in 'backRankMate,hangingPiece,quietMove,advancedPawn,kingsideAttack,attraction,skewer,defensiveMove,discoveredAttack,fork,sacrifice,deflection,pin'.split(','):
            extractDiff(tag)
    
    if False:
        exractDetails()
    
    if False:
        saveLichessModels("rating1000", minSize = 1000, maxSize=200000, moves2Use = 6)
    
    if False:
        checkMistakeOnSavedModels('rating', onlyMistakes = False)
        checkMistakeOnSavedModels('correct', onlyMistakes = False)
    
    if False:
        checkLichessOnSavedModels('pin')
    
    if False:
        for tag in 'fork pin rating crushing advantage'.split():
#         for tag in 'pin rating crushing advantage'.split():
            checkMistakeOnSavedModels(tag)
    
    if False:
        checkMistakeOnGivenMoves('fxe5 Qh5+ g6 Qxe5+ Qe7 Qxh8'.split(), tag = 'fork')
        checkMistakeOnGivenMoves('fxe5 Qh5+ g6 Qxe5+ Qe7 Qxh8'.split(), tag = 'pin')
        checkMistakeOnGivenMoves('fxe5 Qh5+ g6 Qxe5+ Qe7 Qxh8'.split(), tag = 'rating')
        checkMistakeOnGivenMoves('fxe5 Qh5+ g6 Qxe5+ Qe7 Qxh8'.split(), tag = 'crushing')
        checkMistakeOnGivenMoves('fxe5 Qh5+ g6 Qxe5+ Qe7 Qxh8'.split(), tag = 'advantage')
    
    if False:
        for tag in ['fork','pin']:
            saveLichessModels(tag, minSize = 1000, maxSize=200000)
    
    if False:
        for tag in 'short,middlegame,endgame,rating,crushing,advantage,mate,long,fork,mateIn2,oneMove,kingsideAttack,pin,sacrifice,advantage middlegame short,discoveredAttack,opening,hangingPiece,defensiveMove,veryLong,mateIn1,crushing middlegame short,advancedPawn,deflection,rookEndgame,endgame mate mateIn2 short,backRankMate,mateIn3,crushing endgame short,master,attraction,crushing endgame fork short,equality,quietMove,crushing fork middlegame short,advantage fork middlegame short,skewer'.split(','):
            if ' ' in tag:
                continue
            saveLichessModels(tag, minSize = 1000, maxSize=200000)
    
    if False:
        summary = ''
        summary += "BY MOVE:\n"
        summary += classifyTag('rating', byMove = True, moves2Use = 6, maxSize = 200000)
        summary += "\nBY POS:\n"
        summary += classifyTag('rating', byMove = False, moves2Use = 6, maxSize = 200000)
        print (summary)
    
    if False:
        getMoveByDepth()
    
    if False:
        for tag in 'rating,short,middlegame,endgame,crushing,advantage,mate,long,fork,mateIn2,oneMove,kingsideAttack,pin,sacrifice,discoveredAttack,opening,hangingPiece,defensiveMove,veryLong,mateIn1,advancedPawn,deflection,rookEndgame,backRankMate,mateIn3,master,attraction,equality,quietMove,skewer'.split(','):
            classifyTagByPos(tag, maxSize=100000)
            
    if False:
        for tag in 'rating,short,middlegame,endgame,crushing,advantage,mate,long,fork,mateIn2,oneMove,kingsideAttack,pin,sacrifice,discoveredAttack,opening,hangingPiece,defensiveMove,veryLong,mateIn1,advancedPawn,deflection,rookEndgame,backRankMate,mateIn3,master,attraction,equality,quietMove,skewer'.split(','):
            classifyTag(tag, moves2Use = 2, byMove = True, minSize = 10000, maxSize = 100000)
            classifyTag(tag, moves2Use = 4, byMove = True, minSize = 10000, maxSize = 100000)
            classifyTag(tag, moves2Use = 6, byMove = True, minSize = 10000, maxSize = 100000)
    
    if False:
        tooFew = False
        summary = ''
        for tag in 'rating,short,middlegame,endgame,crushing,advantage,mate,long,fork,mateIn2,oneMove,kingsideAttack,pin,sacrifice,discoveredAttack,opening,hangingPiece,defensiveMove,veryLong,mateIn1,advancedPawn,deflection,rookEndgame,backRankMate,mateIn3,master,attraction,equality,quietMove,skewer'.split(','):
            
            if ' ' in tag:
                continue
            
            classifyTag(tag, moves2Use = 2, byMove = True, minSize = 10000, maxSize = 100000)
            classifyTag(tag, moves2Use = 4, byMove = True, minSize = 10000, maxSize = 100000)
            classifyTag(tag, moves2Use = 6, byMove = True, minSize = 10000, maxSize = 100000)
#             summary += "\n*************************\n"
#             summary += tag
#             summary += "\n*************************\n"
#             summary += "BY MOVE (4):\n"
#             summary += classifyTag(tag, moves2Use = 4, byMove = True)
#             summary += "BY MOVE (6):\n"
#             summary += classifyTag(tag, moves2Use = 6, byMove = True)
            if not tooFew:
                summary += "\nBY POS:\n"
                try:
                    classifyTagByPos(tag, maxSize=100000)
#                     summary += classifyTag(tag, byMove = False, minSize = 10000, maxSize=100000)
                except Exception as e:
                    if tooFew:
                        raise e
                    tooFew = True
                
                summary += "\n"
        print (summary)
