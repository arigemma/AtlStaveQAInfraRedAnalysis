#!/usr/bin/env python
"""
@run:
  ./csvToRoot.py path/to/CSVfile.csv [options]
  
  type ./csvToRoot.py -h for help

@brief:
  This script converts the thermal image in the CSV format into a .root file containing
  a TTree objects with three branches for x,y positions and temperatures. 

@reference:
  TTree in python: 
    https://www-zeuthen.desy.de/~middell/public/pyroot/pyroot.html
    https://root.cern.ch/how/how-write-ttree-python

@email: vozdeckyl@gmail.com
"""

import numpy as np
import os
import csv
import logging
import argparse
import ROOT

parser = argparse.ArgumentParser()
parser.add_argument("path", help="The path to the input CSV file")
parser.add_argument("-d","--debug", help="Runs the code in debug mode", action="store_true")
parser.add_argument("-1f","--one_face", help="Run the code with only one stave", action="store_true")
args = parser.parse_args()

inputFile = args.path

if args.one_face:
    print("**********")
    print("This option has not been coded yet. Exiting.")
    print("**********")
    logging.error("The script cannot deal with CSV with just one face.")
    logging.debug("Exiting")
    exit()

#check if the suffix is .csv
if inputFile[-3:] != "csv":
    print("The input file should be a .csv file")
    quit()

#delete the debug folder if it exists and create a new one
if args.debug:
  if "debug_output" in os.listdir("."):
    os.system("rm -r debug_output")
  os.mkdir("debug_output")

#set up the debugging log
if args.debug:
    logging.basicConfig(filename='debug_output/csvToRoot_debug.log',level=logging.DEBUG)

#fetch the CSV file
logging.debug("Opening the CSV file")
imgList = []
with open(inputFile) as csvfile:
    reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
    for row in reader:
        imgList.append(row)
image = np.array(imgList)

logging.debug("Image uploaded as np.array with dimensions {}".format(image.shape))

logging.debug("Splitting the image into two, one for each face")
upper_image = image[:,0:int(image.shape[1]/2)]
lower_image = image[:,int(image.shape[1]/2):int(image.shape[1])]


logging.debug("upper_image.shape = {}".format(upper_image.shape))
logging.debug("shape lower_image = {}".format(lower_image.shape))

temperature = np.empty((1), dtype="float64")
xpos = np.empty((1), dtype="int64")
ypos = np.empty((1), dtype="int64")

logging.debug("(Re)creating a ROOT file")
file_lower = ROOT.TFile("test_lower.root", "recreate")

logging.debug("Creating a TTree with branches.")
atree = ROOT.TTree("atree", "a tree of temperature data")
atree.Branch('temperature', temperature, 'temperature/D')
atree.Branch('xpos', xpos, 'xpos/I')
atree.Branch('ypos', ypos, 'ypos/I')

logging.debug("converting lower image")
for i in range(0,lower_image.shape[0]):
    for j in range(0,lower_image.shape[1]):
        logging.debug("temperature[{}][{}] = {}".format(i,j,lower_image[i][j]))
        temperature[0] = lower_image[i][j]
        xpos[0] = i
        ypos[0] = j
        atree.Fill()

file_lower.Write()

file_lower.Close()
 

file_upper = ROOT.TFile("test_upper.root", "recreate")

atree = ROOT.TTree("atree", "a tree of temperature data")
atree.Branch('temperature', temperature, 'temperature/D')
atree.Branch('xpos', xpos, 'xpos/I')
atree.Branch('ypos', ypos, 'ypos/I')

logging.debug("converting upper image")
for i in range(0,lower_image.shape[0]):
    for j in range(0,lower_image.shape[1]):
        logging.debug("temperature[{}][{}] = {}".format(i,j,lower_image[i][j]))
        temperature[0] = upper_image[i][j]
        xpos[0] = i
        ypos[0] = j
        atree.Fill()

file_upper.Write()

file_upper.Close()
