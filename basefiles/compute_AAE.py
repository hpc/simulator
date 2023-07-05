"""
Usage: 
    compute_AAE.py -d FLOAT -m FLOAT -r FLOAT [-c FLOAT] [--add-dump]

    Required Options:
        -d --dump-time <FLOAT>
        -m --MTBF <FLOAT>
        -r --read-time <FLOAT>
        -c --checkpoint-interval <FLOAT>     if omitted, just does optimal
        --add-dump                           will add dump-time to checkpoint
"""
from docopt import docopt,DocoptExit
import numpy as np
import sys

try:
    args=docopt(__doc__,help=True,options_first=False)
except DocoptExit:
    print(__doc__)
    sys.exit(1)

d=float(args["--dump-time"])
m=float(args["--MTBF"])
r=float(args["--read-time"])
c=float(args["--checkpoint-interval"]) if args["--checkpoint-interval"] else np.sqrt(2*m*d)
a=True if args["--add-dump"] else False
orig=c
if a:
    c=c+d

AAE=np.exp(-r/m) * ((c/m)-(d/m))/(np.exp(c/m) -1)

print()
print("Is dump-time < 1/2 M?  "+str(d<(.5*m))+"  "+str(d)+" <  " + str(.5*m))
print("Checkpoint:            ",orig)
print("Checkpoint - dump:     ",orig-d)
print("Checkpoint + dump:     ",orig+d)
print("AAE should be:         ",AAE)
print()

