#!/usr/bin/env python
import os
import sys
import argparse
import pandas as pd
from collections import defaultdict

"""
Take in top level books directory (and past file to update?)
Create a sheet for each subdirectory, ignore files in top level dir
Each sheet has header: Author Title Filetype
Parse filenames
    os.path.splitext()
    Split name on ' -- '
    If length = 1: Title
    If length = 2: Author Title (or Title Author if textbook)
    If length = 3: Author Series Title
"""

def main(args):
    # Get the subdirectories of the top level directory
    TLD = os.path.abspath(arg.directory)
    dirs = [os.path.join(TLD, d) for d in os.listdir(TLD) if os.path.isdir(d)]
    # Go through each subdirectory to populate sheets
    sheets = {}
    for d in dirs:
        data = defaultdict(list)
        files = os.listdir(d)
        for f in files:
            # Get file type
            ext = os.path.splitext(f)[1][1:].upper()
            fields = os.path.splitext(f)[0].split(' -- ')
            # Parse file names (TO DO)
        sheets[os.basename(d)] = pd.DataFrame(data)
    # Write output index to file
    with pd.ExcelWriter(outfile) as f:
        for sheet, df in sheets.items():
            df.to_excel(f, sheet_name=sheet, index=False, freeze_panes=(1,0))
    print("Done!")

if __name__ =="__main__":
    desc = ("Indexes the contents of the provided Books directory. The spreadsheet "
            "output will be placed in the provided directory. One sheet will be created "
            "for each subfolder of the top level Books directory. If an existing index "
            "is provided, the contents will be updated with any new additions.")
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-i', '--index', help="Path to existing index to update.")
    parser.add_argument('-o', '--output', default="Index", help="Name for the output index file. Default: Index")
    parser.add_argument('directory', help="Top level Books directory to index.")
    args = parser.parse_args()
    if not os.path.isdir(args.directory):
        sys.exit("The specified directory does not exist: {}".format(args.directory))
    if args.index and not os.path.isfile(args.index):
        sys.exit("The specified file does not exist: {}".format(args.index))
    main(args)

