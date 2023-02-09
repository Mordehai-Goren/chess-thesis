import zipfile

from os import listdir
from os.path import isfile, join

pgnmentor_folder = 'C:/dev/tools/workspace/fics/pgnmentor/'
zipFolder = pgnmentor_folder + 'zip'
pgnFolder = pgnmentor_folder + 'pgn'

def extractZipFiles(zipFolder):
    onlyfiles = [f for f in listdir(zipFolder) if isfile(join(zipFolder, f))]
    print (onlyfiles)
    
    for f in onlyfiles:
        if f.endswith(".zip"):
            with zipfile.ZipFile(zipFolder + "//" + f, 'r') as zip_ref:
                zip_ref.extractall(zipFolder)
                

def allPgn2OneFile(pgnFolder):
    onlyfiles = [f for f in listdir(pgnFolder) if isfile(join(pgnFolder, f))]
    print (onlyfiles)
    
    with open('pgnmentor.pgn', 'w') as w:
        for f in onlyfiles:
            if f.endswith(".pgn"):
                with open(pgnFolder + "/" + f, 'r') as r:
                    game = ''
                    for l in r:
                        l = l.strip()
                        if l.startswith('1.'):
                            game = l
                        else:
                            game += " " + l
                        if l.endswith('1-0') or l.endswith('0-1') or l.endswith('1/2-1/2'):
                            game = game.replace('.', ' ')
                            moves = [m for m in game.split() if m and not m.isnumeric()]
                            game = ' '.join(moves)
                            w.write(game)
                            w.write("\n")
                            
        
 
if __name__=='__main__':
#     extractZipFiles(zipFolder)
    allPgn2OneFile(pgnFolder)