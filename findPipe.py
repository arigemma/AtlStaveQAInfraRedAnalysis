#!/usr/bin/env python

import ROOT
import argparse
#import logging
from frameanal import FrameAnalysis

parser = argparse.ArgumentParser()
parser.add_argument("path", help="The path to the input ROOT file")
parser.add_argument("-d","--debug", help="Runs the code in debug mode", action="store_true")
args = parser.parse_args()


if args.path[-4:] != "root":
  print("The input file should be a .root file")
  quit()


name = args.path[:-5].split("/")[-1]

analysis = FrameAnalysis(args.path, "ThermalImpedanceQA/output/config_{}_top".format(name), "ThermalImpedanceQA/output", False, False)

analysis.find_pipes()
