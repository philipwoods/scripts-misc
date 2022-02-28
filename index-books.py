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
"""
def parse_filename(filename):
    """
    Arguments
    ---------
    filename: str
        A string containing the base name of the file
        Format: [Author -- ][Series -- ]Title.ext
        Title must be present. Author may be present.
        If Series is present, Author must also be present.

    Returns
    -------
    tuple
        Contains author, series, title, file type
    """
    # Get the extension and the sections of the filename
    name, ext = os.path.splitext(f)
    ext = ext[1:].upper() # We don't want the .
    fields = name.split(' -- ')
    # Parse the filename
    # If length = 1: Title
    # If length = 2: Author Title
    # If length = 3: Author Series Title
    if len(fields) == 1:
        author, series, title = "", "", fields[0]
    elif len(fields) == 2:
        author, series, title = fields[0], "", fields[1]
    elif len(fields) == 3:
        author, series, title = fields
    return (author, series, title, ext)

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
            # Parse file names
            (author, series, title, ext) = parse_filename(f)
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

