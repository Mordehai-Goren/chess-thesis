import file_util as U

def extract_file_data(gameInput, toPrint = 10):
    count = 0
    print ('First %s lines'%toPrint)
    l = None
    with open(gameInput, 'r') as f:
        for l in f:
            if count < toPrint:
                print (l)
            count += 1
    
    print ()
    print ('last line: ')
    print (l)
    print ()
    print ('number of lines')
    print (count)

def countCorrectIncorrect(gameInput):
    countCorrectMoreThan5 = 0
    countLines = 0
    moreThan5 = 0
    with open(gameInput, 'r') as f:
        for l in f:
            countLines += 1
            dbID, correct, fen, san, nextSan, uci, nextUci = l.split('|')
            
            san = san.split()
            nextSan = nextSan.split()
            
            if len(san)>=5 and len(nextSan)>=5:
                moreThan5+=1
            
                if correct=='True':
                    countCorrectMoreThan5+=1
            
    print (countLines)
    print (moreThan5)
    print (countCorrectMoreThan5)
    print (moreThan5 - countCorrectMoreThan5)
    


if __name__=='__main__':
    extract_file_data(U.WALL_RAW, 1)
#     extract_file_data(U.FICS_RAW, 1)
#     extract_file_data(U.CHESS_DB_RAW, 1)
#     extract_file_data(U.FICS_STRONG_RAW, 1)
#     extract_file_data(U.MISTAKE_RAW)
#     countCorrectIncorrect(U.MISTAKE_RAW)