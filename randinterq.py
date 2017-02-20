import os
import sys
import errno
import random
import glob
import tkinter
from tkinter import filedialog
import pyautogui
import time
import configparser

root = tkinter.Tk()
root.withdraw()

#Setting current Dir
dir_path = os.path.dirname(os.path.realpath(__file__))


#Move mouse to upper left screen to kill in case of error
pyautogui.FAILSAFE = True

autokeytemplate = ("""import subprocess
import os
os.chdir("{0}")
subprocess.call("python randinterq.py {1}", shell=True)
""")

autokeyjsontemplate = ("""{{
    "type": "script",
    "description": "{0}",
    "store": {{}},
    "modes": [
        1
    ],
    "usageCount": 0,
    "prompt": false,
    "omitTrigger": false,
    "showInTrayMenu": false,
    "abbreviation": {{
        "abbreviations": [
            "{1}"
        ],
        "backspace": true,
        "ignoreCase": false,
        "immediate": false,
        "triggerInside": false,
        "wordChars": "[^\\t]"
    }},
    "hotkey": {{
        "modifiers": [],
        "hotKey": null
    }},
    "filter": {{
        "regex": null,
        "isRecursive": false
    }}
}}""")

ahktemplate = ("""
::{0}::
SetWorkingDir, {1}
Run %comspec% /c ""{2}" "{3}"",,hide
return
""")

config = configparser.ConfigParser()
ahkpath = 'none'
autokeypath = 'None'
qpath = dir_path


if os.path.isfile('config.ini'):
    config.sections()
    config.read('config.ini')
    ahkpath = config['Default']['ahkdir']
    autokeypath = config['Default']['autokeydir']
    qpath = config['Default']['qdir']


def createdir():
    numdir = int(input("Please enter the number of questions (directories) you would like: "))
    a = 0
    while a <= numdir:
        dir_name = ("Question %s" % a)
        try:
            os.mkdir(dir_name)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        a = a + 1
    passfail = input("Would you like to create the pass/fail directories? (y/n): ")
    if passfail == 'y':
        try:
            os.mkdir("Question pass")
            os.mkdir("Question fail")
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise


def writerandomq():
    script, qnum = sys.argv
    os.chdir(qpath)
    #Create list of filenames
    search_path = os.path.join('Question %s' % qnum, '*.txt')
    filenames = glob.glob(search_path)

    #Open Random file from list
    selqfile = open(random.choice(filenames))
    qcontent = selqfile.read()

    #Write content of file
    pyautogui.typewrite(qcontent)

def genautokey():
    gen = input("\nDo you wish to generate the python autokey files? (y/n): ")
    numq = None
    if gen == 'y':
        print("\nI recommend using question 0 as the intro of your interview script."
              "\nIt will be created along with the other questions.")
        numq = int(input("\nPlease enter the number of questions you have: "))
        a = 0
        os.chdir(autokeypath)
        while a <= numq:
            f = open("question%s.py" % a, "w")
            f.write(autokeytemplate.format(dir_path, a))
            a = a + 1
            f.close()
        f = open("pass.py", "w")
        f.write(autokeytemplate.format(dir_path, 'pass'))
        f.close()
        f = open("fail.py", "w")
        f.write(autokeytemplate.format(dir_path, 'fail'))
        f.close()
    gjson = input("Do you wish to generate the .json files as well? (y/n): ")
    if gjson == 'y':
        if numq == None:
            numq = int(input("\nPlease enter the number of questions you have: "))
        b = 0
        os.chdir(autokeypath)
        while b <= numq:
            f = open(".question%s.json" % b, "w")
            f.write(autokeyjsontemplate.format('Question %s' % b, 'q%s'% b))
            f.close()
            b = b + 1
        f = open(".pass.json", "w")
        f.write(autokeyjsontemplate.format('pass', 'pass'))
        f.close()
        f = open(".fail.json", "w")
        f.write(autokeyjsontemplate.format('fail', 'fail'))
        f.close()
        leaving()
    else:
        leaving()

def genahk():
    numq = None
    print("\nI recommend using question 0 as the intro of your interview script."
          "It will be created along with the other questions.")
    numq = int(input("\nPlease enter the number of questions you have: "))
    a = 0
    os.chdir(ahkpath)
    filename = os.path.splitext(os.path.basename(__file__))[0]
    with open("randinterq.ahk", "w") as file:
        file.write('#Hotstring EndChars `t')
        while a <= numq:
            file.write(ahktemplate.format('q%s' % a, dir_path, '%s.exe' % filename, a))
            a = a + 1
        file.write(ahktemplate.format('pass', dir_path, '%s.exe' % filename, 'pass'))
        file.write(ahktemplate.format('fail', dir_path, '%s.exe' % filename, 'fail'))
    leaving()

def leaving():
    os.chdir(dir_path)
    config['Default'] = {}
    config['Default']['ahkdir'] = ahkpath
    config['Default']['autokeydir'] = autokeypath
    config['Default']['qdir'] = qpath
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    print("\nFor normal use of this program, please pass the number of the question you would like to write")
    print("For example: 'randinterq 11' will return a random selection from question 11")
    print("Will exit in 5 seconds")
    time.sleep(5)
    exit()

if len(sys.argv) == 1:
    print("\nWelcome to the Apollo.rip Interviewer Companion app!")
    choosedir = input("\nWould you like to change the location of the question folders? (y/n): ")
    if choosedir == 'y':
        qpath = filedialog.askdirectory(initialdir='.')
    makedir = input("Do you wish to make some directories to hold your question files? (y/n): ")
    if makedir == 'y':
        os.chdir(qpath)
        createdir()
    windows = input("Are you running windows and using autohotkey? (y/n): ")
    if windows == 'y':
        ahkchangedir = input("Do you wish to set/change where the ahk script is saved? (y/n): ")
        if ahkchangedir == 'y':
            ahkpath = filedialog.askdirectory(initialdir='.')
        startgenahk = input("Do you wish to create the ahk script? (y/n): ")
        if startgenahk == 'y':
            genahk()
    linux = input("Are you running linux and using AutoKey? (y/n): ")
    if linux == 'y':
        autochangedir = input("Do you wish to set/change the AutoKey directory? (y/n): ")
        if autochangedir == 'y':
            linuxrdy = input("\nPress y when you are ready to set the AutoKey directory \n \n"
                             "Make sure this folder was already created by AutoKey previously \n"
                             "otherwise press any other key to exit: ")
            if linuxrdy == 'y':
                autokeypath = filedialog.askdirectory(initialdir='.')
                genautokey()
            else:
                leaving()
        else:
            genautokey()
#    if linux == 'n':
#        leaving()
    else:
        leaving()
else:
    writerandomq()
