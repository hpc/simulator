#!/usr/bin/env python3
"""

Will take an original failures file and an '.../output/' PATH and go through finding the first failures.csv that does not match up

Usage:
    compare_failures.py -o PATH -i PATH

Required Options:
    -o PATH --original PATH         The absolute path to the original failures.csv file

    -i PATH --input PATH            The path to the '.../output/' folder in question

"""
import pathlib
import pandas as pd
import json
import re
import sys
import os
import subprocess
scriptPath = str(pathlib.Path(__file__).parent.absolute())
sys.path.append(str(pathlib.Path(scriptPath).parent.absolute()))
from docopt import docopt
args=docopt(__doc__,help=True,options_first=False)
import functions
originalFile = args["--original"]
inputFolder = args["--input"]
inputFolder = str(pathlib.Path(inputFolder).absolute())
folders = [f"{i}" for i in os.listdir(inputFolder) if os.path.isdir(f"{inputFolder}/{i}")]
folder_numbers=[]
max_folder=0
for folder in folders:
    split_folder=folder.split("_")
    if len(split_folder) == 2:
        folder_numbers.append(int(split_folder[1]))
if len(folder_numbers) >= 1:
    max_folder = max(folder_numbers)
for i in range(max_folder,-1,-1):
    end=f"_{i}"
    if i == 0:
        end=""
    command = subprocess.Popen(["/usr/bin/bash","-c",f"wc -l {inputFolder}/expe-out{end}/failures.csv | awk '{{print $1}}'"],stdout=subprocess.PIPE)
    lines,err = command.communicate()
    lines = int(lines.decode('utf-8'))
    command = subprocess.Popen(["/usr/bin/bash","-c",f"head -n {lines} {originalFile} > {originalFile}_{i}"])
    command.communicate()
    command = subprocess.Popen(["/usr/bin/bash","-c",f"sed -E 's@\$[0-9]+@@g' {inputFolder}/expe-out{end}/failures.csv > {inputFolder}/expe-out{end}/failures.csv_{i}"])
    command.communicate()
    command = subprocess.Popen(["/usr/bin/bash","-c",f"diff {originalFile}_{i} {inputFolder}/expe-out{end}/failures.csv_{i}"],stdout=subprocess.PIPE)
    out,err = command.communicate()
    command = subprocess.Popen(["/usr/bin/bash","-c",f"rm {originalFile}_{i} {inputFolder}/expe-out{end}/failures.csv_{i}"])
    command.communicate()
    if len(out) > 0:
        print(out.decode('utf-8'))
        print(f"{inputFolder}/expe-out{end}")
        sys.exit(1)
sys.exit(0)
