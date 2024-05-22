#!/usr/bin/env python3
"""
Program to snip out sections of [log] files

Usage:
    edit_text.py --input <PATH> --regex <STR> [--output <PATH>]

Required Options:
    -i <PATH> --input <PATH>                The input file

    --regex <STR>                           The regex to snip.  Currently not used, hardcoded
Optional Options:   
    -o <PATH> --output <PATH>               Where to output
                                            [default: inplace]
"""
from docopt import docopt,DocoptExit
import sys
import re
import signal
def signal_handler(signum,frame):
    with open(outputFile,mode="w",encoding="utf8") as file_obj:
        file_obj.write(text)
    sys.exit(1)
def signal_handler2(signum,frame):
    with open(outputFile,mode="w",encoding="utf8") as file_obj:
        file_obj.write(text)

#get our docopt options read in
try:
    args=docopt(__doc__,help=True,options_first=False)
except DocoptExit:
    print(__doc__)
    sys.exit(1)

inputRegEx = str(args["--regex"])
inputFile = args["--input"]
outputFile = args["--output"] if args["--output"] != "inplace" else inputFile
signal.signal(signal.SIGINT,signal_handler)
signal.signal(signal.SIGQUIT,signal_handler2)

# if inputFile == outputFile:
#     with open(inputFile, mode="r+", encoding="utf8") as file_obj:
#         with mmap.mmap(file_obj.fileno(), length=0, access=mmap.ACCESS_WRITE) as mmap_obj:
#             text = mmap_obj.read()
#             inputRegEx="schedule[.]cpp[:]2635((.|\n)*?)easy_bf2[.]cpp[:]318"
#             regEx = re.compile(inputRegEx)
#             matches = regEx.search(text)
#             while (matches != None):
#                 mmap_obj[matches.start():matches.end()]=""
#                 mmap_obj.flush()
#                 text = mmap_obj.read()
#                 matches = regEx.search(text)
# else:
#     with open(inputFile, mode="r", encoding="utf8") as file_obj:
#         with mmap.mmap(file_obj.fileno(), length=0, access=mmap.ACCESS_READ) as mmap_obj:
#             text = mmap_obj.read()
#             inputRegEx="schedule[.]cpp[:]2635((.|\n)*?)easy_bf2[.]cpp[:]318"
#             regEx = re.compile(inputRegEx)
#             matches = regEx.search(text)
#             while (matches != None):
#                 text=text[:matches.start()]+text[matches.end():]
#                 matches = regEx.search(text)
#     with open(outputFile,mode="w",encoding="utf8") as file_obj:
#         file_obj.write(text)
with open(inputFile, mode="r", encoding="utf8") as file_obj:
    text = file_obj.read()

inputRegEx="schedule[.]cpp[:]2635((.|\n)+?)easy_bf2[.]cpp[:]318"
regEx = re.compile(inputRegEx)
matches = regEx.search(text)
count=1
while (matches != None):
    lines = text.count("\n")
    print(f"Match: {count:,}  Text Length: {len(text):,}   Lines: {lines:,}")
    count+=1
    text=text[:matches.start()]+text[matches.end()-18:]
    matches = regEx.search(text,matches.start())
with open(outputFile,mode="w",encoding="utf8") as file_obj:
    file_obj.write(text)



