#! /usr/bin/python

__version__ = "0.2"
__author__  = "Florent Baume"

import glob, os, csv
import pySpire as ps
import re

###############################################################
### FUNCTIONS
###############################################################

absDir=os.path.dirname(os.path.realpath(__file__))
##
## IMPORTANT: THE FOLLOWING LINE DEFINES PARENTS DIRECTORY AS SEARCH DIRECTORY
##
#absDir=os.path.dirname(absDir)
fileList=[f for f in os.listdir(absDir) if f.endswith(".pdf")]

print(fileList)

def write_csv(fList):
    """Prepares a HTML string for a given ArXiV identifier. """
    idList=[re.search("(" + ps.reEprint + ")", f ).group(1) for f in fList if re.search("(" + ps.reEprint + ")", f ) is not None]
    dicList=[ps.get_arxiv_data(id) for id in idList]
    dicKeys=list(set.union(*[set(d.keys()) for d in dicList ]))
    keys=["title","author","eprint","bibkey"]
    keys.extend([k for k in dicKeys if k not in keys])
    
    with open('Paper_List.csv', 'w', newline='') as csvfile:
        writer=csv.DictWriter(csvfile,fieldnames=keys,delimiter="\t")
        writer.writeheader()
        for d in dicList:
            writer.writerow(d)

write_csv(fileList)
