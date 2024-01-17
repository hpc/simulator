#!/usr/bin/env python3
"""
Usage:
    alphabetize_json.py -i <PATH> [-o <NEW_PATH>]

Required Options:
    -i, --input <PATH>            Where json lives.  By default, will edit in-place

Optional Options
    -o, --output <NEW_PATH>       The path to the new file
"""
from docopt import docopt,DocoptExit
import functions
import sys
import os
import json

def dictHasKey(myDict,key):
    if key in myDict.keys():
        return True
    else:
        return False
def json_dumps_sorted(data, **kwargs):
    sorted_keys = kwargs.get('sorted_keys', tuple())
    if not sorted_keys:
        return json.dumps(data)
    else:
        out_list = []
        for element in data:
            element_list = []
            for key in sorted_keys:
                if key in element:
                    element_list.append(json.dumps({key: element[key]}))
            out_list.append('{{{}}}'.format(','.join((s[1:-1] for s in element_list))))
        return '[{}]'.format(','.join(out_list))

try:
    args=docopt(__doc__,help=True,options_first=False)
except DocoptExit:
    print(__doc__)
    sys.exit(1)
scriptPath = os.path.expanduser(str(os.path.dirname(os.path.abspath(__file__)))).rstrip("/")
path = args["--input"]
if path[0] != "/":
    path = scriptPath + "/" + path
output = args["--output"] if args["--output"] else path
if output[0] != "/":
    output = scriptPath +"/" + output
with open(path,"r") as InFile:
    myJson = json.load(InFile)
myKeyOrder=["type","required","regex",\
            "real_start","true_real_start","false_real_start",\
            "batsim","true_batsim","false_batsim",\
            "batsched","true_batsched","false_batsched"]
myJson = functions.sortJson(myJson,"all",keyOrder=myKeyOrder,default="alphabetic")


with open(output,"w") as OutFile:
    json.dump(myJson,OutFile,indent=4)