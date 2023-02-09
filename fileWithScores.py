import stockfish_util as S
import file_util as F
import time

start_time = time.time()

# shalow = Engine(depth = 7, param = {'multiPV':2})
# deep = Engine(depth = 14, param = {'multiPV':2})

def timeScoreFileCreation(filename):
    count = 0
    start_time = time.time()
    
    with open(filename, 'r') as f:
        for l in f:
            l = l.split()
            moves = l[:-1]
            outcome = l[-1]
            
            if outcome not in ['1-0', '0-1']:
                continue
            
            count+=1
            
            count += len(moves)
            
            try:
                scoresPerMove = S.getScorePerMove(moves)
            except Exception as e:
                print (' '.join(l))
                continue
            scoresPerMove += '%s\n'%outcome
            
            if (count > 10000):
                break
    took = time.time() - start_time
    print (filename)
    print (count)
    print (took)
            
def createScoresFile(filename, start = ''):
    count = 0
    scoreFile = filename.replace('.pgn', '_score.pgn%s'%start)
    with open(filename, 'r') as f:
        with open(scoreFile, 'w') as w:
            for l in f:
                l = l.split()
                moves = l[:-1]
                outcome = l[-1]
                
                if outcome not in ['1-0', '0-1']:
                    continue
                
                count+=1
                if start and count < start:
                    continue
#                 print (' '.join(l))
                
                try:
                    scoresPerMove = S.getScorePerMove(moves)
                except Exception as e:
                    print (' '.join(l))
                    continue
                scoresPerMove += '%s\n'%outcome
                w.write(scoresPerMove)
                
                if not count % 10:
                    print (count)
                    print (time.time()-start_time)

if __name__=='__main__':
    if True:
        timeScoreFileCreation(F.PGN_MENTOR_RAW)
        timeScoreFileCreation(F.FICS_RAW)
    
    if False:
        createScoresFile(F.PGN_MENTOR_RAW)
#     createScoresFile(F.WALL_RAW)
#     createScoresFile(F.FICS_RAW, start = 62009)
#     createScoresFile(F.CHESS_DB_RAW, start = 64179)
#     createScoresFile(F.FICS_STRONG_RAW, start=64180)