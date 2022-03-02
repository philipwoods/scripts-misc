#!/usr/bin/env python
import os
import sys
import argparse
import pandas as pd
from collections import defaultdict

"""
Take in top level books directory (and past file to update?)
Create a sheet for each subdirectory, ignore files in top level dir
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
        Contains author, title, series, file type
    """
    # Get the extension and the sections of the filename
    name, ext = os.path.splitext(filename)
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
    return (author, title, series, ext)

def main(args):
    # Get the subdirectories of the top level directory
    TLD = os.path.abspath(args.directory)
    contents = [os.path.join(TLD, entry) for entry in os.listdir(TLD)]
    dirs = [d for d in contents if os.path.isdir(d)]
    # Go through each subdirectory to populate sheets
    sheets = {}
    for d in dirs:
        data = defaultdict(list)
        files = os.listdir(d)
        for f in files:
            # Parse file names
            (author, title, series, ext) = parse_filename(f)
            # Add to the data dictionary
            data['Filename'].append(f) # Used as an index to compare entries
            data['Author(s)'].append(author)
            data['Title'].append(title)
            if os.path.basename(d) == 'Novels': # I only care about series for novels
                data['Series'].append(series)
            data['Type'].append(ext)
        sheets[os.path.basename(d)] = pd.DataFrame(data)
    # Write output index to file
    outfile = os.path.join(TLD, args.output + ".xlsx")
    with pd.ExcelWriter(outfile, engine='xlsxwriter') as writer:
        # Set up formatting objects
        workbook = writer.book
        left_fmt = workbook.add_format({'align': 'left', 'border': 0})
        center_fmt = workbook.add_format({'align': 'center', 'border': 0})
        column_widths = {
                'Filename': 10,
                'Author(s)': 40,
                'Title': 90,
                'Series': 20,
                'Type': 10
                }
        column_styles = {
                'Filename': left_fmt,
                'Author(s)': left_fmt ,
                'Title': left_fmt ,
                'Series': left_fmt ,
                'Type': center_fmt
                }
        # Write in data
        for sheet, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet, index=False, freeze_panes=(1,0))
            # Format data nicely
            (max_row, max_col) = df.shape
            cols = {col: list(df.columns).index(col) for col in df.columns}
            worksheet = writer.sheets[sheet]
            worksheet.autofilter(0, 0, max_row, max_col - 1)
            for c in df.columns:
                if c == 'Filename':
                    worksheet.set_column(cols[c], cols[c], column_widths[c], column_styles[c], {'hidden': True})
                else:
                    worksheet.set_column(cols[c], cols[c], column_widths[c], column_styles[c])
    print("Done!")

if __name__ =="__main__":
    desc = ("Indexes the contents of the provided Books directory. The spreadsheet "
            "output will be placed in the provided directory. One sheet will be created "
            "for each subfolder of the top level Books directory. If an existing index "
            "is provided, the contents will be updated with any new additions.")
    epil = ("Note: The --index option is not yet implemented.")
    parser = argparse.ArgumentParser(description=desc, epilog=epil)
    parser.add_argument('-i', '--index', help="Path to existing index to update.")
    parser.add_argument('-o', '--output', default="Index", help="Name for the output index file. Default: Index")
    parser.add_argument('directory', help="Top level Books directory to index.")
    args = parser.parse_args()
    if not os.path.isdir(args.directory):
        sys.exit("The specified directory does not exist: {}".format(args.directory))
    if args.index and not os.path.isfile(args.index):
        sys.exit("The specified file does not exist: {}".format(args.index))
    main(args)

