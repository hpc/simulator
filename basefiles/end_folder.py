"""
    Usage:
        end_folder.py   --folder PATH
        
    Required Options:
        --folder PATH       a folder to change permissions of while inside docker container
                            so we can delete files
"""
import os
import sys
from docopt import docopt

args=docopt(__doc__,help=True,options_first=False)

print("making things deletable")
os.system("chmod 775 -R /home/sim/shared/"+args['--folder'])
os.system("chmod 775 -R /home/sim/base/")
