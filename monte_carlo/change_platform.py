"""
Usage:
    change_platform.py [options]

Options:
    -i FILE --input FILE    where the platform file is
                            [default: /home/sim/base/platforms/platform.xml]
    -o FILE --output FILE   where the output platform file should go
                            [default: input]
    --nodes <INT>           change the cluster 'my_cluster_1'
                            to have radical = '0-(INT -1)'
"""


from docopt import docopt
from xml.etree import ElementTree as ET

args=docopt(__doc__,help=True,options_first=False)
lastNode=int(args["--nodes"])-1
platform_file=args["--input"]
platform_out_file=args["--output"] if not args["--output"] == "input" else args["--input"]

tree = ET.parse(platform_file)
clusters=tree.findall('zone/cluster')
for cluster in clusters:
    if cluster.get("id") == "my_cluster_1":
        cluster.set("radical","0-{lastNode}".format(lastNode=lastNode))

string = ET.tostring(tree.getroot(),method='xml').decode()
doctype = "<!DOCTYPE platform SYSTEM \"http://simgrid.gforge.inria.fr/simgrid/simgrid.dtd\">"
xmlver = "<?xml version='1.0'?>"
string = xmlver + "\n" +  doctype + "\n" + string
with open(platform_out_file,"w") as outfile:
    outfile.write(string)
