#! /usr/bin/python

__version__ = "0.2"
__author__  = "Florent Baume"

import re
import urllib.request
import os, sys
import csv


##################################################
# FUNCTIONS
##################################################

reEprint="\d\d\d\d\.\d{4,5}"
reOldEprint="[a-zA-Z\-\.]*/\d{7}"

def check_arxiv_format(identifier):
    identifier= identifier.replace('arxiv:','')
    # Decides type of ArXiV format.
    # (Must be exactly one of the two 0706.0001.pdf not accepted.)
    if re.search("^" + reOldEprint +"$",identifier): #e.g. math.GT/0309136
        identifierType="pre0704-eprint"
    elif re.search("^" + reEprint +"$",identifier):  #e.g. 0706.0001
        identifierType="eprint"
    else: 
        identifierType="other"
    return identifier, identifierType

def get_arxiv_data(identifier):
    """Gets Inspire record as a dictionary from a ArXiv number"""

    identifier, idType = check_arxiv_format(identifier)
    
    # determines query. Gives place for adding other 
    if idType == "eprint": 
        query= "?p=find+eprint+?" + identifier
    else: raise ValueError("ArXiV identifier " + identifier + " not valid (NB: pre 0704 identifier not accepted without prefix).")

    # Get html source from ArXiv number.
    with urllib.request.urlopen("http://inspirehep.net/search" + query + "&of=hx") as response: htmlSource=response.read().decode("utf-8")
    # Get BibTeX code from html source.
    bibtexCode=re.search("(^@\w+{\w+:\d+\w+[\S\s]*?^\})",htmlSource, flags = re.MULTILINE)
    # Creates dictionary for the record with bibkey entry.
    ref={"bibkey" : re.search("^@\w+{(\w+:.+),",bibtexCode.group(), flags = re.MULTILINE).group(1) }
    # Get all entries and add them to dictionary. Removes characters.
    matches = re.findall("((\w+)\s*=\s*\"([^\"]+)\")",bibtexCode.group(), flags = re.MULTILINE)
    for m in matches: ref[m[1]]=re.sub( "\n\s+", " ", m[2] ).strip().replace("{","").replace("}","")

    return ref


def retrieve_arxiv_list(fpath):
    """Retrieves multiple ArXiv numbers from a csv file as 
    a list of dictionaries."""
    
    arxivNumbers=[]
    with open(fpath) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for l in csv_reader: arxivNumbers.append(l[0])
    return [get_arxiv_data(an) for an in arxivNumbers]

def author_lists(ref):
    """Returns nested list of authors from a dictionary."""
 
    matches = re.findall("(\S+)(?:,\s+)(\S+)",ref["author"])
    return matches
