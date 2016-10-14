#!/usr/bin/env python

"""
stufftracker.py

Gary L & Matty J

tracks stuff for you
"""

from lxml.etree import parse, XMLParser, ElementTree, Element, SubElement, XMLSyntaxError
from flask import Flask, render_template, request
from sys import platform as _platform
import os

app = Flask(__name__)

if _platform == "linux" or _platform == "linux2":
    INVENTORY = "inv/inventory.xml"
    CONFIG = "etc/config.txt" 
else:
    INVENTORY = "inv/inventory.xml"
    CONFIG = "etc/config.txt"

def get_mug_number(config_path=CONFIG):
    with open(config_path) as config:
        for line in config:
            configtype = line.split('=')[0]
            configvalue = line.split('=')[1].strip()
            if configtype == 'numberOfMugs':
                mug_number = int(configvalue)

    return mug_number

def get_stuff(mug_number):
    """
    reads inventory file and returns list of checked out/checked in stuff!
    """
    
    try:
        parser = XMLParser(remove_blank_text = True)
        inv = parse(INVENTORY, parser)
        root = inv.getroot()
        currentnumber = len(root[0])
        if mug_number != currentnumber:
            os.remove(INVENTORY)
            raise IOError

    except IOError:
        #if none, or empty file

        root = Element('inventory')
        inv = ElementTree(root)
        item = SubElement(root, 'mugs')
        for serial_number in range(1, mug_number+1):
            mug = SubElement(item, 'mug', checkedin='True')
            mug.text = repr(serial_number)

        inv.write(INVENTORY, pretty_print = True)
        
        return get_stuff(mug_number)
        
    except XMLSyntaxError:
        os.remove(INVENTORY)

        return get_stuff(mug_number)
    else:
        ret_val = dict()
        
        current_mugs = 0
        for item in root:
            for mug in item:
                if mug.get("checkedin") == 'True':
                    ret_val[int(mug.text)] = True
                else:
                    ret_val[int(mug.text)] = False

    return ret_val

def update_stuff(req=request):
    
    parser = XMLParser(remove_blank_text = True)
    inv = parse(INVENTORY, parser)
    root = inv.getroot()
    
    current_mugs = 0
    for item in root:
        for mug in item:
            if request.form.get(mug.text) == '1':
                mug.set("checkedin", "True")
            else:
                mug.set("checkedin", "False")

    inv.write(INVENTORY, pretty_print = True)   

@app.route("/", methods = ['GET', 'POST'])
def main():
    
    mug_number = get_mug_number()
    if request.form:
        update_stuff()

    mugs_dict = get_stuff(mug_number)
     
    return render_template("bdc.html", mugs = mugs_dict)


if __name__ == "__main__":
    app.run(use_debugger = True)
