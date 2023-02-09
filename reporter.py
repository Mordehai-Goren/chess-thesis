from datetime import datetime
from file_util import LOG_FOLDER


label = ''
def setLabel(l):
    global label
    label = l

filename = LOG_FOLDER + "%s.log"%(datetime.now().strftime('%y%m%d%H%M%S'))
def report(message):
    global label
    with open(filename, 'a') as a:
        a.write(label)
        a.write(' '.join(message.split()))
        a.write("\n")
    
if __name__=='__main__':
#     dateTimeObj = datetime.now()
#     timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
#     print('Current Timestamp : ', timestampStr)
#     print (filename)
    report("Hi")
    report("Hello\n world")
    setLabel("HaHA")
    report("look at me")