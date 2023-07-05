"""
Usage:
    stripJsonComments.py --input FILE --output FILE

Required Option:
    --input FILE     The file to strip
    --output FILE    The file to output
"""

def stripComments(myString,kind="C"):
    import re
    if kind == "C" or "all":
        inlineComments = re.findall(r'//.*$',myString,re.MULTILINE)
        for comment in inlineComments:
            myString = myString.replace(comment,"")
        blockComments = re.findall(r'/[*].*?[*]/',myString,re.DOTALL)
        for comment in blockComments:
            myString = myString.replace(comment,"")
    if kind == "python" or "all":
        inlineComments = re.findall(r'[#].*$',myString,re.MULTILINE)
        for comment in inlineComments:
            myString = myString.replace(comment,"")
    return myString
def loadFile(inputFile):
    
    data = open(inputFile,"r")
    myString = data.read()
    data.close()

    return myString
def saveFile(outputFile,myString):
    data = open(outputFile,"w")
    data.write(myString)
    data.close()




from docopt import docopt,DocoptExit
import sys

#get our docopt options read in
if __name__ == '__main__':   
    try:
        args=docopt(__doc__,help=True,options_first=False)
    except DocoptExit:
        print(__doc__)
        sys.exit(1)

    inputFile=args["--input"]
    outputFile=args["--output"]
    myString = loadFile(inputFile)
    myString = stripComments(myString)
    #saveFile(outputFile,myString)





