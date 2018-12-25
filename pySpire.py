#! /usr/bin/python

__version__ = "0.1"
__author__  = "Florent Baume"

import re, urllib.request

#def get_page(query):
#    """Gets the source from URL from a arxiv number"""
#
#def get_Bibtex(source):
#    return re.search("(^@\w+{\w+:\d+\w+[\S\s]*?^\})",source, flags = re.MULTILINE)
#

def get_arxiv_data(query):
    """Gets Inspire record as a dictionary from a ArXiv number"""

    # Get html source from ArXiv number.
    with urllib.request.urlopen("http://inspirehep.net/search?p=find+eprint+?" + query + "&of=hx") as response: htmlSource=response.read().decode("utf-8")
    # Get BibTeX code from html source.
    bibtexCode=re.search("(^@\w+{\w+:\d+\w+[\S\s]*?^\})",htmlSource, flags = re.MULTILINE)
    # Creates dictionary for the record with bibkey entry.
    ref={"bibkey" : re.search("^@\w+{(\w+:.+),",bibtexCode.group(), flags = re.MULTILINE).group(1) }
    # Get all entries and add them to dictionary. Removes characters.
    matches = re.findall("((\w+)\s*=\s*\"([^\"]+)\")",bibtexCode.group(), flags = re.MULTILINE)
    for m in matches: ref[m[1]]=re.sub( '\n\s+', ' ', m[2] ).strip().replace("{","").replace("}","")

    return ref

print(get_arxiv_data("1709.07453"))
