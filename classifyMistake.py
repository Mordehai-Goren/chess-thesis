import game_2_features as F
import file_util as U
import classifier as C
import metrics as M
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from joblib import dump, load
import reporter as R
# import time

def classifyMistake(featureFile, before = 5, after = 5, testSize = 1000, trainSize = 100000, all = False, frameworks = None):
    print ("Start %s; Before: %s; After: %s\n"%(featureFile, before, after))
    summary = "%s; Before: %s; After: %s\n"%(featureFile, before, after)
    
    data = F.loadFeatureFile(featureFile)
    
    xTrain = []; yTrain = []; countTrain = 0
    xTest = []; yTest = []; countTest = 0
    
    #Can also work without this...
    np.random.shuffle(data)

    #Later to be used
    featuresPerMove = F.FEATURES_PER_MOVE
    
    for entry in data:
        if all:
            x = entry[1:]
        else:
            x = entry[1 + (5-before)*featuresPerMove : 1 + 5*featuresPerMove + after*featuresPerMove]
            
            print (len(x))
            
#         x = entry[1:]
#         print (len(x))
        y = entry[0]
        
        if countTest < testSize:
            xTest.append(x); yTest.append(y); countTest += 1
            continue
        
        if countTrain < trainSize:
            xTrain.append(x); yTrain.append(y); countTrain += 1
            continue
        
    xTrain = np.array(xTrain); yTrain = np.array(yTrain)
    xTest = np.array(xTest); yTest = np.array(yTest)
    
    print ("Test: %s. Train: %s"%(countTest, countTrain))
    summary += "Test: %s. Train: %s\n"%(countTest, countTrain)
    
    if not frameworks:
        frameworks = ['nb', 'rf', 'ann']
        
    
#     frameworks = ['nb', 'rf', 'ann']
#     frameworks = ['ann', 'rnn']
#     frameworks = ['nb', 'rf', 'ann', 'svm']
#     frameworks = ['svm']
#     summary += "Before: %s; After: %s; \n"%(before, after)
    summary += M.summarizerPerFrameworkAllOn1(frameworks, xTrain, yTrain, xTest, yTest)
    print ("Done %s; Before: %s; After: %s"%(featureFile, before, after))
    return summary

mm = {}
for m in 'abcdefgh':
    mm[m] = 'P'
    
for m in 'rnbqkp':
    mm[m.upper()] = m.upper()
#     mm[m] = m.upper()

mm['O'] = 'K'

cmm = {}

for m in 'abcdefgh':
    cmm[m] = 'P'

for m in 'rnbqkp':
    cmm[m] = m.upper()
    cmm[m.upper()] = m.upper()

def simplify(san, uci):
    try:
        piece = mm[san[0]]
        captured = cmm[san.split('x')[1][0]] if 'x' in san else '_' 
        check = '+' if san[-1]=='+' or san[-1]=='#' else '_'
    except:
        print (san)
        print (uci)
        raise
    
#     #En pesant fashla
#     if captured=='B' and (san[0]=='a' or san[0]=='c') and (san[3]=='6' or san[3]=='3'):
#         captured = 'P'
    return piece + uci[0:2] + captured + uci[2:4] + check 

def saveSimplified():  
    correctCount = 0
    count = 0
    
    with open(U.MISTAKE_RAW + ".simp", 'w') as w:
        with open(U.MISTAKE_RAW, 'r') as r:
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
                
                beforeUci = uci.split()[-5:]
                afterUci = nextUci.split()[:5]
                
                w.write('1 ' if correct else '0 ')
                
                for san, uci in zip(before, beforeUci):
                    w.write(simplify(san, uci))
                    w.write(' ')
                    
                for san, uci in zip(after, afterUci):
                    w.write(simplify(san, uci))
                    w.write(' ')
                
                w.write("\n")
            
                count+=1
    print (count)


d = {'R':[1,0,0,0,0,0],
     'N':[0,1,0,0,0,0],
     'B':[0,0,1,0,0,0],
     'Q':[0,0,0,1,0,0],
     'K':[0,0,0,0,1,0],
     'P':[0,0,0,0,0,1],
     '_':[0,0,0,0,0,0]}

for i,c in enumerate('abcdefgh'):
    d[c]=[i+1]
    
for i,c in enumerate('12345678'):
    d[c]=[i+1]

UCI =            [1,1,1,1,1,0,0]
ALL =            [1,1,1,1,1,1,1]
UCI_NO_ROW =     [1,0,1,1,1,0,0]
UCI_NO_COL =     [1,1,0,1,1,0,0]
UCI_NO_ROW_COL = [1,0,0,1,1,0,0]
UCI_NO_CAPTURE = [1,1,1,0,1,0,0]
UCI_NO_CHECK =   [1,1,1,1,0,0,0]
SAN =            [0,1,1,0,0,0,1]

PIECE = 0; COL = 1; ROW = 2; CAPTURE = 3; CHECK = 4; CAP_PIECE = 5; FROM = 6;
def simpMove2Feature(m, features2use):
    features = []
    
    if (features2use[PIECE]):
        features += d[m[0]]
        
    if (features2use[COL]):
        features += d[m[4]]
        
    if (features2use[ROW]):
        features += d[m[5]]
        
    if (features2use[CAPTURE]):
        features += [0] if m[3]=='_' else [1]
        
    if (features2use[CAP_PIECE]):
        features += d[m[3]]
        
    if (features2use[FROM]):
        features += d[m[1]]
        features += d[m[2]]
        
    if (features2use[CHECK]):
        features += [0] if m[6]=='_' else [1]
    
    return features

n2c = {}
for i,c in enumerate('abcdefgh'):
    n2c[i+1]=c 
    
#UCI
def feature2Move(feature):
    moves = ''
    for increment in (0, 10, 20):
#     for increment in (0, 10, 20, 30, 40, 50, 60, 70, 80, 90):
        for i, piece in enumerate('RNBQKP'):
            if feature[increment+i]:
                break
        col = n2c[feature[increment+6]]
#         col = str(feature[increment+6])
        row = str(feature[increment+7])
        capture = 'x' if feature[increment+8] else ''
        check = '+' if feature[increment+9] else ''
        moves += piece + capture + col + row + check + "^"
    return moves
    

testSize = 10000
trainSize = 90000 
def classifyMistakeVar(before = 5, after = 5, features2use = UCI, frameworks = ['nb', 'rf', 'ann'], before1After1_3 = False):
    xTrain = []; yTrain = []; countTrain = 0
    xTest = []; yTest = []; countTest = 0
    
    toPrint = True
    
    if before1After1_3:
        before = 1
        after = 3
    
    with open(U.MISTAKE_RAW + ".simp", 'r') as f:
        for l in f:
            entry = l.split()
            
            y = int(entry[0])
            moves = entry[6-before : 6 + after]
            
            if before1After1_3:
                moves = [moves[0], moves[1], moves[3]]
            
            x = []
            for m in moves:
                x += simpMove2Feature(m, features2use)
                
                if moves[0]=="Bb4Nc3+" and toPrint:
#                 if toPrint:
                    print (simpMove2Feature(m, features2use))
            
            if moves[0]=="Bb4Nc3+" and toPrint:
#             if toPrint:
                print (x)
                print (l)
                print (moves)
                print (before, after)
                toPrint = False
            
            x = np.array(x)
            
            if countTrain < trainSize:
                xTrain.append(x); yTrain.append(y); countTrain += 1
                continue
        
            if countTest < testSize:
                xTest.append(x); yTest.append(y); countTest += 1
                continue
    
    xTrain = np.array(xTrain); yTrain = np.array(yTrain)
    xTest = np.array(xTest); yTest = np.array(yTest) 
    
#     frameworks = ['rf']
#     frameworks = ['nb', 'rf', 'ann']
#     frameworks = ['ann', 'rnn']
#     frameworks = ['nb', 'rf', 'ann', 'svm']
#     summary += "Before: %s; After: %s; \n"%(before, after)
    summary = M.summarizerPerFrameworkAllOn1(frameworks, xTrain, yTrain, xTest, yTest)
    print (summary)

def testClassificationOnLiChess(testSize = 1000, trainSize = 100000, save = False):
    print ("Start testClassificationOnLiChess")
    before = 1
    after = 5
#     data = F.loadFeatureFile(featureFile)

    print ("Start %s; Before: %s; After: %s\n"%(U.MISTAKE, before, after))
    summary = "%s; Before: %s; After: %s\n"%(U.MISTAKE, before, after)
    
    data = F.loadFeatureFile(U.MISTAKE)
    
    xTrain = []; yTrain = []; countTrain = 0
    xTest = []; yTest = []; countTest = 0
    
    #Can also work without this...
    np.random.shuffle(data)

    #Later to be used
    featuresPerMove = F.FEATURES_PER_MOVE
    
    for entry in data:
        x = entry[1 + (5-before)*featuresPerMove : 1 + 5*featuresPerMove + after*featuresPerMove]
#         x = entry[1:]
#         print (len(x))
        y = entry[0]
        
#         if countTest < testSize:
#             xTest.append(x); yTest.append(y); countTest += 1
#             continue
        
        if countTrain < trainSize:
            xTrain.append(x); yTrain.append(y); countTrain += 1
            continue
        
    xTrain = np.array(xTrain); yTrain = np.array(yTrain)
#     xTest = np.array(xTest); yTest = np.array(yTest)
    
    model = RandomForestClassifier(n_estimators=100)
    model.fit(xTrain, yTrain)
    
    if save:
        dump(model, U.MODEL_GAME_FOLDER + save)
    
    
    data = F.loadFeatureFile(U.LICHESS)
    
    count = 0
    for entry in data:
        x = entry[2:]
        
        if len(x)!=6*10:
            xTest.append(xTrain[0])
            continue
        
        xTest.append(x); countTest += 1
        if count < 10:
            print (x)
            count += 1
    xTest = np.array(xTest); 
    
#     model = C.classify('rf', xTrain, yTrain)
    probabilities = model.predict_proba(xTest)
    predictions = model.predict(xTest)
    
    count = 0
    with open("li_chess_prob.csv", 'w') as w:
        for (prob, p) in zip(probabilities,predictions):
            if True:
                w.write('%s\n'%prob[1])
                if count < 100:
                    print (prob[1], p)
                count += 1
                if count > 200000:
                    break

if __name__=='__main__':
    
    
    if False:
        R.setLabel("ClassifyMistakeByPosition")
        classifyMistake(U.MISTAKE_FEN, all = True)
        
        
    if False:
        R.setLabel("before1After1_3^%s^"%("UCI"))
        classifyMistakeVar(before1After1_3 = True, features2use = UCI, frameworks = ['svm'])
        
        R.setLabel("before5After5^%s^"%("UCI"))
        classifyMistakeVar(before = 5, after = 5, features2use = UCI, frameworks = ['svm'])
        
        R.setLabel("before1After1_3^%s^"%("ALL"))
        classifyMistakeVar(before1After1_3 = True, features2use = ALL, frameworks = ['svm'])
        
        R.setLabel("before5After5^%s^"%("ALL"))
        classifyMistakeVar(before = 5, after = 5, features2use = ALL, frameworks = ['svm'])
        
    
    if False:
        print (simpMove2Feature('Bb2Bc3_', SAN))
        
    
    if False:
        R.setLabel("before1After1_3")
        classifyMistakeVar(before1After1_3 = True, features2use = UCI, frameworks = ['rf'])
    
    if False:
        R.setLabel("before1After1_3^%s^"%("UCI"))
        classifyMistakeVar(before1After1_3 = True, features2use = UCI)
        
        R.setLabel("before1After1_3^%s^"%("ALL"))
        classifyMistakeVar(before1After1_3 = True, features2use = ALL)   
                                              
        R.setLabel("before1After1_3^%s^"%("SAN"))
        classifyMistakeVar(before1After1_3 = True, features2use = SAN)
                 
        R.setLabel("before1After1_3^%s^"%("UCI_NO_ROW"))
        classifyMistakeVar(before1After1_3 = True, features2use = UCI_NO_ROW)   
                     
        R.setLabel("before1After1_3^%s^"%("UCI_NO_COL"))
        classifyMistakeVar(before1After1_3 = True, features2use = UCI_NO_COL)  
                      
        R.setLabel("before1After1_3^%s^"%("UCI_NO_ROW_COL"))
        classifyMistakeVar(before1After1_3 = True, features2use = UCI_NO_ROW_COL)  
                      
        R.setLabel("before1After1_3^%s^"%("UCI_NO_CAPTURE"))
        classifyMistakeVar(before1After1_3 = True, features2use = UCI_NO_CAPTURE)  
                      
        R.setLabel("before1After1_3^%s^"%("UCI_NO_CHECK"))
        classifyMistakeVar(before1After1_3 = True, features2use = UCI_NO_CHECK)
    
    if False:
        before = after = 5
        R.setLabel("%s^%s^%s^"%(before, after, "UCI_NO_ROW_COL"))
        classifyMistakeVar(before = before, after = after, features2use = UCI_NO_ROW_COL, frameworks = ['nb'])
        
    
    if False:
        before = after = 5
        R.setLabel("%s^%s^%s^"%(before, after, "ALL"))
        classifyMistakeVar(before = before, after = after, features2use = ALL, frameworks = ['svm'])
    
    if True:
        before = after = 5
        R.setLabel("Importance^%s^%s^%s^"%(before, after, "UCI"))
        classifyMistakeVar(before = before, after = after, features2use = UCI, frameworks = ['rf'])
    
    if False:
        for before in range(6):
            for after in range(6):
                
                if not before and not after:
                    continue
                
                R.setLabel("%s^%s^%s^"%(before, after, "UCI"))
                classifyMistakeVar(before = before, after = after, features2use = UCI)
                
                R.setLabel("%s^%s^%s^"%(before, after, "ALL"))
                classifyMistakeVar(before = before, after = after, features2use = ALL)   
                                                      
                R.setLabel("%s^%s^%s^"%(before, after, "SAN"))
                classifyMistakeVar(before = before, after = after, features2use = SAN)
                         
                R.setLabel("%s^%s^%s^"%(before, after, "UCI_NO_ROW"))
                classifyMistakeVar(before = before, after = after, features2use = UCI_NO_ROW)   
                             
                R.setLabel("%s^%s^%s^"%(before, after, "UCI_NO_COL"))
                classifyMistakeVar(before = before, after = after, features2use = UCI_NO_COL)  
                              
                R.setLabel("%s^%s^%s^"%(before, after, "UCI_NO_ROW_COL"))
                classifyMistakeVar(before = before, after = after, features2use = UCI_NO_ROW_COL)  
                              
                R.setLabel("%s^%s^%s^"%(before, after, "UCI_NO_CAPTURE"))
                classifyMistakeVar(before = before, after = after, features2use = UCI_NO_CAPTURE)  
                              
                R.setLabel("%s^%s^%s^"%(before, after, "UCI_NO_CHECK"))
                classifyMistakeVar(before = before, after = after, features2use = UCI_NO_CHECK)

    if False:
        print (mm)
    
    if False:
        saveSimplified()
    
    if False:
        testClassificationOnLiChess(testSize = 100, trainSize = 30000, save = 'correct')
    
    if False:
        testClassificationOnLiChess()
#     data = F.loadFeatureFile(U.MISTAKE)
#     print (data[0])
#     print (len(data[0]))
#     summary = classifyMistake(U.MISTAKE, before = 5, after = 5)
#     summary = classifyMistake(U.MISTAKE_FEN, all = True)
    
#     summary = '\n\n============================\n\n'
#     summary += classifyMistake(U.WALL.replace(".pgn", "_50.fen"), all = True)
#     summary += classifyMistake(U.CHESS_DB.replace(".pgn", "_50.fen"), all = True)
#     summary += classifyMistake(U.PGN_MENTOR.replace(".pgn", "_50.fen"), all = True)
#     summary += classifyMistake(U.FICS_STRONG.replace(".pgn", "_50.fen"), all = True)
#     summary += classifyMistake(U.FICS.replace(".pgn", "_50.fen"), all = True)
    
#     summary += classifyMistake(U.WALL.replace(".pgn", "_50.fen.pgn"), all = True)
#     summary += classifyMistake(U.CHESS_DB.replace(".pgn", "_50.fen.pgn"), all = True)
#     summary += classifyMistake(U.PGN_MENTOR.replace(".pgn", "_50.fen"), all = True)
# #     summary += classifyMistake(U.FICS_STRONG.replace(".pgn", "_50.fen"), all = True)
# #     summary += classifyMistake(U.FICS.replace(".pgn", "_50.fen"), all = True)
#     
# 
#     print (summary)
    
    if False:
        summary = classifyMistake(U.MISTAKE_FEN, all = True)
        summary += "\n---------------------------\n"
        for before in range(6):
            for after in range(6):
                if not before and not after:
                    continue
                summary += classifyMistake(U.MISTAKE, before, after)
                
        print (summary)
    
    
