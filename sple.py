#! /usr/bin/python

__version__ = "0.2"
__author__  = "Florent Baume"

import sys, os, csv, argparse
import pySpire as ps
import json
from pyld import jsonld
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

###############################################################
### FUNCTIONS
###############################################################

def write_arxiv(identifier):
    """Prepares a HTML string for a given ArXiV identifier. """
    dic=ps.get_arxiv_data(identifier)
    authors=", ".join([d[0] for d in ps.author_lists(dic)])
    str="<i>{title},</i> "+authors+", <a href=\"https://arxiv.org/abs/{eprint}\" target=\"_blank\">ArXiV link</a>"
    str=str.format(**dic)
    return str

def retrieve_arxiv_list(fpath):
    """Retrieves multiple ArXiv numbers from a csv file and
    creates the list for the email as a string"""
    
    arxivNumbers=[]
    with open(fpath) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for l in csv_reader: arxivNumbers.append(l[0])
    return 0 

def update_time():
    date=datetime.datetime.strptime(repString["datetime"],"%Y-%m-%dT%H:%M")
    repString["date"] = date.strftime("%Y-%m-%d")
    repString["time"] = date.strftime("%H:%M")
    repString["weekday"] = date.strftime("%A")
        
def update_dict(fname):
    # Open csv and actualise keys.
    with open(fname, mode='r') as infile:
        reader = csv.reader(infile,delimiter=',')
        for line in reader: 
            if len(line)<=2:
                repString[line[0]] = line[1].lstrip()
            else:
                repString[line[0]]=line[1:]
            
            if line[0] == "arxivIDs":
                repString["paper-list"] = introPaperList + "\n        ".join(
                        ["<p>(" + str(n) + ") " + write_arxiv(st) + 
                            "</p>" for (n,st) in enumerate([ l.replace(" ","") for l in line[1:]],start=1)
                        ]
                )
    update_time()


def prepare_email(dic):
    """Prepares the general email data."""
    with open(dic["emailFile"].replace(" ",""), mode='r') as infile:
        core=infile.read().format(**dic)
    return core

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":"yes",   "y":"yes",  "ye":"yes",
             "no":"no",     "n":"no"}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while 1:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")

def get_email_addresses():
    with open(repString["addressFile"], mode='r') as infile:
        lines = list(filter(None, [line.rstrip() for line in infile]))
    if isinstance(lines,str):
        return lines
    else:
        return lines

def sendemail(recipients,subject,body):
    
    # Get credentials from the file given in argument -p.
    with open(args.p, mode='r') as infile:
        credentials = list(filter(None, [line.rstrip() for line in infile]))
    
    # Prepares arguments of emails.
    msg = MIMEMultipart()
    msg['From'] = credentials[0]
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))
    text = msg.as_string()

    # Sends the emails.
    server = smtplib.SMTP('smtp.gmail.com', 587, None, 30)
#    server = smtplib.SMTP_SSL('smtpinterno.uam.es', 587, None, 30)
    server.ehlo()
    server.starttls()
    server.ehlo()
    print(credentials)
    server.login(*credentials)
    server.set_debuglevel(True)  # show communication with the server
    server.sendmail(credentials[0], recipients, text)
    server.quit()

###############################################################
### DEFAULT VALUES
###############################################################




defaultIntro="<p>We will have another installment of the SPLE journal club next week.</p>"
defaultRoom="discussion room on the fourth floor (B418)"
introPaperList="<p>During this episode of the journal club, we will discuss the following papers:</p>\n        "

repString={
    "intro"       : defaultIntro, 
    "room"        : defaultRoom,
    "datetime"    : "2019-01-01T11:30",
    "title"       : "",
    "arxivIDs"    : "",
    "addressFile" : "emailAddress.txt",
    "emailFile"   : "email.html",
    "addendum"    : "",
    "paper-list"  : ""
}
update_time()

###############################################################
### ARGUMENTS AND OTHER INTERACTIONS WITH USER
###############################################################

parser=argparse.ArgumentParser(description=
        '''This script generates an email from a csv file for the SPLE journal club at the IFT Madrid.'''
    )

parser.add_argument(
        "--csv",
        type=str,
        metavar = "file.csv",
        default=os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "config.csv"
            ),
        help="File from which data is read (default: 'config.csv' in script directory)"
        )

parser.add_argument(
        "-t",
        type=int,
        metavar = "n",
        default=0,
        help="Type of email sent. 0: general; 1: reminder (default: 0)"
        )

parser.add_argument(
        "-p",
        type=str,
        metavar = "pwd.txt",
        help="File from which username and password are read. They must be on two different lines"
        )
args=parser.parse_args()
# Updates the dictionary with data from configFile
update_dict(args.csv)

###############################################################
### SEND EMAIL
###############################################################

# Ask the user to check the email (in html).
coreCheck=query_yes_no(
        "The prepared email has been generated and is the following:\n\n"
        +prepare_email(repString)
        +"\n Do you want to proceed? "
        , default=None
)

if coreCheck == "yes":
    addressesCheck=query_yes_no(
        "The above email will be sent to the following recipient(s):\n\n"
        +"\n".join(get_email_addresses())
        +"\n\nDo you want to proceed? "
        , default=None)
    print(get_email_addresses())
    if addressesCheck=="yes":
        print("Sending emails...")
        sendemail(get_email_addresses(), repString["title"], prepare_email(repString))
        print("Emails sent !")
    else:
        print("Aborting...")
else:
    print("Aborting...")
