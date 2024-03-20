import pandas as pd
import numpy as np
import json
from docopt import docopt
import sys
import os
import datetime as dt
import re
import time

def dictHasKey(myDict,key):
    if key in myDict.keys():
        return True
    else:
        return False
def testCheckpointing(ourInput,nb_sims):
    progressFile = f"{ourInput}/progress.log"
    notDone=True
    simsSuccess = 0
    simsCount = 0
    while (notDone):
        simsCount = 0
        simsSuccess = 0
        with open(progressFile,"r") as InFile:
            progress = json.load(InFile)
        for key in progress:
            if key[-4:] == "post":
                simsCount += 1
                simsSuccess += int(progress[key])
        print(f"simsCount: {simsCount} simsSuccess: {simsSuccess}",flush=True)
        if simsCount == nb_sims:
            notDone = False
        else:
            time.sleep(30)
    # ok we have all the sims finished.  Lets make sure they all ended successfully
    if simsSuccess == nb_sims:
        return True

    else:
        print(f"Error: We had {nb_sims} sims to complete, but only {simsSuccess} sims finished successfully")
        return False
