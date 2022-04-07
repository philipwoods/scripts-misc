#!/usr/bin/env python
import os
import sys
import argparse
import pandas as pd
from collections import defaultdict

def make_lalign_formatter(df, cols=None):
    """
    Construct formatter dict to left-align columns.

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        The DataFrame to format
    cols : None or iterable of strings, optional
        The columns of df to left-align. The default, cols=None, will
        left-align all the columns of dtype object

    Returns
    -------
    dict : Formatter dictionary

    """
    if cols is None:
       cols = df.columns[df.dtypes == 'object'] 
    return {col: f'{{:<{df[col].str.len().max()}s}}'.format for col in cols}

def print_changed_files(df, cols=['Filename']):
    """
    Print properly formatted list of changed files.

    Parameters
    -------------
    df : pandas.core.frame.Dataframe
        A dataframe containing index entries for the changed files.
    cols : list
        A list containing the string names of the column(s) to print.

    Returns
    -------------
    None, prints to stdout
    """
    print(df.to_string(columns=cols, index=False, header=False, formatters=make_lalign_formatter(df)))

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

def write_index(sheets, outfile):
    """
    Arguments
    -----------
    sheets: dict
        A dictionary where each key is the name
        of a sheet in the index, and each value
        is a DataFrame containing the data for
        that sheet.
    outfile: str
        A string containing the file path
        where the index will be written.

    Returns
    -----------
    None
    """
    with pd.ExcelWriter(outfile, engine='xlsxwriter') as writer:
        # Set up formatting objects
        workbook = writer.book
        left_fmt = workbook.add_format({'align': 'left', 'border': 0})
        center_fmt = workbook.add_format({'align': 'center', 'border': 0})
        colors = {
                'red_bg': '#FFD7D7',
                'yellow_bg': '#FFF5CE',
                'green_bg': '#DDE8CB',
                'blue_bg': '#DEE6EF',
                'purple_bg': '#E0C2CD',
                '2_scale_min': '#FFEF9C',
                '2_scale_max': '#FF7128',
                'neutral_txt': '#996600',
                'neutral_bg': '#FFFFCC',
                'good_txt': '#006600',
                'good_bg': '#CCFFCC',
                'bad_txt': '#CC0000',
                'bad_bg': '#FFCCCC'
                }
        red_bg = workbook.add_format({'bg_color': colors['red_bg']})
        yellow_bg = workbook.add_format({'bg_color': colors['yellow_bg']})
        green_bg = workbook.add_format({'bg_color': colors['green_bg']})
        blue_bg = workbook.add_format({'bg_color': colors['blue_bg']})
        purple_bg = workbook.add_format({'bg_color': colors['purple_bg']})
        good_fmt = workbook.add_format({'bg_color': colors['good_bg'], 'font_color': colors['good_txt']})
        neutral_fmt = workbook.add_format({'bg_color': colors['neutral_bg'], 'font_color': colors['neutral_txt']})
        bad_fmt = workbook.add_format({'bg_color': colors['bad_bg'], 'font_color': colors['bad_txt']})
        # These dictionaries contain information for all columns in any sheet.
        # Not all columns must be present in each sheet.
        column_order = {
                'Filename': 1,
                'Type': 2,
                'Author(s)': 3,
                'Title': 4,
                'Series': 5,
                'Category': 6,
                'Field': 7,
                'Subfield': 8,
                'Importance': 9,
                'Enthusiasm': 10,
                'Read?': 11
                }
        column_widths = {
                'Filename': 10,
                'Type': 8,
                'Author(s)': 30,
                'Title': 70,
                'Series': 20,
                'Category': 15,
                'Field': 20,
                'Subfield': 20,
                'Importance': 12,
                'Enthusiasm': 12,
                'Read?': 8
                }
        column_styles = {
                'Filename': left_fmt,
                'Type': center_fmt,
                'Author(s)': left_fmt,
                'Title': left_fmt,
                'Series': left_fmt,
                'Category': center_fmt,
                'Field': left_fmt,
                'Subfield': left_fmt,
                'Importance': center_fmt,
                'Enthusiasm': center_fmt,
                'Read?': center_fmt
                }
        # Write in data
        for sheet, df in sheets.items():
            # Reorder columns properly before output
            ordered_cols = sorted(df.columns, key=lambda x: column_order[x])
            df = df[ordered_cols]
            df.to_excel(writer, sheet_name=sheet, index=False, freeze_panes=(1,0))
            # Format data nicely
            (max_row, max_col) = df.shape
            cols = {col: list(df.columns).index(col) for col in df.columns}
            worksheet = writer.sheets[sheet]
            worksheet.autofilter(0, 0, max_row, max_col - 1)
            # Apply column widths and other styles
            for c in df.columns:
                if c == 'Filename':
                    worksheet.set_column(cols[c], cols[c], column_widths[c], column_styles[c], {'hidden': True})
                else:
                    worksheet.set_column(cols[c], cols[c], column_widths[c], column_styles[c])
            # Set condional formatting to color code by file type
            if 'Type' in df.columns:
                worksheet.conditional_format(0, cols['Type'], max_row, cols['Type'], {'type': 'cell',
                                                                                      'criteria': '==',
                                                                                      'value': '"PDF"',
                                                                                      'format': red_bg})
                worksheet.conditional_format(0, cols['Type'], max_row, cols['Type'], {'type': 'cell',
                                                                                      'criteria': '==',
                                                                                      'value': '"EPUB"',
                                                                                      'format': blue_bg})
                worksheet.conditional_format(0, cols['Type'], max_row, cols['Type'], {'type': 'cell',
                                                                                      'criteria': '==',
                                                                                      'value': '"MOBI"',
                                                                                      'format': yellow_bg})
            # Set conditional formatting color scales for Importance and Enthusiasm
            if 'Importance' in df.columns:
                worksheet.conditional_format(0, cols['Importance'], max_row, cols['Importance'], {'type': '2_color_scale',
                                                                                                  'min_type': 'num',
                                                                                                  'max_type': 'num',
                                                                                                  'min_value': 1,
                                                                                                  'max_value': 5,
                                                                                                  'min_color': colors['2_scale_min'],
                                                                                                  'max_color': colors['2_scale_max']})
            if 'Enthusiasm' in df.columns:
                worksheet.conditional_format(0, cols['Enthusiasm'], max_row, cols['Enthusiasm'], {'type': '2_color_scale',
                                                                                                  'min_type': 'num',
                                                                                                  'max_type': 'num',
                                                                                                  'min_value': 1,
                                                                                                  'max_value': 5,
                                                                                                  'min_color': colors['2_scale_min'],
                                                                                                  'max_color': colors['2_scale_max']})
            # Set conditional formatting to color code by whether I've read it
            if 'Read?' in df.columns:
                worksheet.conditional_format(0, cols['Read?'], max_row, cols['Read?'], {'type': 'cell',
                                                                                        'criteria': '==',
                                                                                        'value': '"N"',
                                                                                        'format': neutral_fmt})
                worksheet.conditional_format(0, cols['Read?'], max_row, cols['Read?'], {'type': 'cell',
                                                                                        'criteria': '==',
                                                                                        'value': '"Y"',
                                                                                        'format': good_fmt})

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
            data['Type'].append(ext)
            data['Author(s)'].append(author)
            data['Title'].append(title)
            if os.path.basename(d) == 'Novels': # I only care about series for novels
                data['Series'].append(series)
        sheets[os.path.basename(d)] = pd.DataFrame(data).set_index('Filename', drop=False)
    # If an existing index was provided...
    if args.index is not None:
        # Read in the old index data
        old_index = pd.read_excel(args.index, sheet_name=None)
        # Reindex the DataFrame on unique file names
        for sheet, df in old_index.items():
            old_index[sheet] = df.set_index('Filename', drop=False)
        # Merge old index with new data
        merged = {}
        all_sheets = sorted(list(set(sheets.keys()).union(set(old_index.keys()))))
        for x in all_sheets:
            print("Merging sheet: {}".format(x))
            print("-"*40)
            if x not in sheets:
                merged[x] = old_index[x]
                print("Directory '{}' not found. Sheet preserved from old index.".format(x))
                print("\tFormer contents:")
                print_changed_files(merged[x], cols=['Filename'])
            elif x not in old_index:
                merged[x] = sheets[x]
                changes = sheets[x]
                print("New directory '{}' found. Sheet added to index.".format(x))
                print("\tContents:")
                print_changed_files(merged[x], cols=['Filename'])
            else:
                merged[x] = sheets[x].combine_first(old_index[x])
                changes = pd.merge(sheets[x], old_index[x], how='outer', left_index=True, right_index=True, indicator=True, validate='one_to_one', suffixes=('_l','_r'))
                print("Changes to directory '{}'.".format(x))
                added = changes[changes['_merge'] == "left_only"]
                removed = changes[changes['_merge'] == "right_only"]
                if not added.empty:
                    print("\tFiles added:")
                    print_changed_files(added, cols=['Filename_l'])
                if not removed.empty:
                    print("\tFiles removed:")
                    print_changed_files(removed, cols=['Filename_r'])
            print("")
        sheets = merged
    # Write output index to file
    outfile = os.path.join(TLD, args.output + ".xlsx")
    write_index(sheets, outfile)
    print("Done!")
    print("\tMake sure to check the spreadsheet entries for any sheets or files listed above!")

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

