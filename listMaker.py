#! /usr/bin/python

__version__ = "0.3"
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


def write_csv(fList):
    """Prepares a csv file for a list of pdfs. """
    idList=[]
    print("Extracting metadata from Inspire...")
    # Extract metadata from inspire
    for f in fList:
        if re.search("(" + ps.reEprint + ")", f ) is None: 
            print("Couldn't extract ArXiV identifier from filename: " + f + ". Proceeding...")
        else:
            idList.append(re.search("(" + ps.reEprint + ")", f ).group(1))
    dicList=[ps.get_arxiv_data(id) for id in idList]
    dicKeys=list(set.union(*[set(d.keys()) for d in dicList ]))
    keys=["title","author","eprint","bibkey"]
    keys.extend([k for k in dicKeys if k not in keys])
    
    print("Exporting csv file...")
    with open(os.path.join(absDir,'Paper_List.csv'), 'w', newline='') as csvfile:
        writer=csv.DictWriter(csvfile,fieldnames=keys,delimiter="\t")
        writer.writeheader()
        for d in dicList:
            writer.writerow(d)
    print("File written!")

fileList=sorted([f for f in os.listdir(absDir) if f.endswith(".pdf")])
# Quits if the directory does not contain any pdf.
if len(fileList)==0: 
    print("Directory does not contain any pdf. Aborting...")
    exit()
else:
    print("There are "+str(len(fileList)) + " pdf(s) in the folder.")
write_csv(fileList)
