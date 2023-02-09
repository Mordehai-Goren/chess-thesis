import numpy as np
import time
import classifier as C
import game_2_features as F
import reporter as R
import classifyMistake as m
import classifyOutcome as o

def getAccNTime(framework, xTrain, yTrain, xTest, yTest, outputs = 2):
    start_time = time.time()
    model = C.classify(framework, xTrain, yTrain, outputs)
    took = time.time() - start_time
    
    xForTest = np.array(xTest)
    yForTest = np.array(yTest)
    
    if False:
        start_time = time.time()
        accuracy = C.evaluate(framework, model, xForTest, yForTest)
        took1 = time.time() - start_time
        print ("PREDICTIONS: %s"%took1)
    else:
        accuracy = C.evaluate(framework, model, xForTest, yForTest)
        
    if False:
        if framework=='rf':
            print (accuracy)
            importance = model.feature_importances_
            R.report('%s'%round(100*accuracy,2))
            for i in range(int(len(importance)/10)):
                s = importance[i*10:i*10+10]
                R.report('%s^%s'%(i,round(100*sum(s),2)))
                print (i, round(100*sum(s),2))
#             print (model.feature_importances_)
            print (len(xTest[0]))
            
    if False:
        if framework=='rf':
            importance = model.feature_importances_
            R.report('%s'%importance)
            
            
    if True:
        if framework=='rf':
            prob = model.predict_proba(xTrain)
            
            R.report("m1^m2^m3^m4^actual^predict")
            
            for x,y,p in zip(xTest, yTest, prob):
                p = p[0]
                if p==0 or p==1:
#                     R.report('^%s%s^%s'%(x,y,(1-p)))
                    R.report('%s%s^%s'%(o.feature2Move(x),y,(1-p)))
#                     R.report('^%s%s^%s'%(m.feature2Move(x),y,(1-p)))
        
#     accuracy = round(accuracy, 2)
    
    return accuracy, took

def saveMetricsPerFramework(xTrain, yTrain, xTest, yTest, tookDict, accrDict, key, outputs = 2):
    for framework in ('ann', 'rf', 'svm', 'stockfish', 'nb', 'rnn'):
#     for framework in ('rf', 'svm'):
        if framework not in tookDict:
            continue
        
        accuracy, took = getAccNTime(framework, xTrain, yTrain, xTest, yTest, outputs)
        
#         print (accuracy)
        tookDict[framework][key] = took
        accrDict[framework][key] = accuracy
    return tookDict, accrDict


def summarizerPerFrameworkAllOn1(frameworks, xTrain, yTrain, xTest, yTest):
#     acc = {};tooks = {}
    sum = ''
    for framework in frameworks:
        acc, took = getAccNTime(framework, xTrain, yTrain, xTest, yTest)
        acc = round(acc, 4)
        print ("%s. Accuracy: %s. Took: %s"%(framework,acc,took ))
        sum += "Framework^%s^Accuracy^%s^Took^%s\n"%(framework,acc,took )
        R.report("Framework^%s^Accuracy^%s^Took^%s\n"%(framework,acc,took ))
#         acc[framework] = accuracy; tooks[framework] = took
    return sum
#     return acc, tooks

def summarizerPerFramework(countPerLength, tookDict, accrDict):
    sum = ""
    for framework in ('ann', 'rf', 'svm', 'stockfish', 'nb', 'rnn'):
#     for framework in ('rf', 'svm'):
        
        if framework not in tookDict:
            continue
        
        countAll = 0
        sumTook = 0
        sumAcc = 0
        
        for gameLength in range(1, 101):
            if gameLength not in countPerLength:
                continue
            
            count = countPerLength[gameLength]
            
            sumTook += tookDict[framework][gameLength]
            acc = accrDict[framework][gameLength]
            
            countAll += count
            sumAcc += count * acc
            
        acc = sumAcc / countAll 
        
        R.report("Framework^%s^Accuracy^%s^Took^%s\n"%(framework,acc,sumTook ))
        sum += "Framework^%s^Accuracy^%s^Took^%s\n"%(framework,acc,sumTook )
        print ("%s. Accuracy: %s. Took: %s"%(framework,acc,sumTook ))
    return sum  

def classifyAsIs(featureFile, testSize = 1000, trainSize = 100000, frameworks = ['nb', 'rf', 'ann']):
    print ("Start %s"%(featureFile))
    summary = "\n===\n%s\n"%featureFile
    
    data = F.loadFeatureFile(featureFile)
    
    xTrain = []; yTrain = []; countTrain = 0
    xTest = []; yTest = []; countTest = 0
    
    #Can also work without this...
    np.random.shuffle(data)
    
    for entry in data:
        x = entry[1:]
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
    R.report("Test^%s^Train^%s\n"%(countTest, countTrain))
    
    summary += summarizerPerFrameworkAllOn1(frameworks, xTrain, yTrain, xTest, yTest)
    print ("Done %s"%(featureFile))
    return summary
      

if __name__=='__main__':
    pass