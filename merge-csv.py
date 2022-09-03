#!/usr/bin/env python
import os
import sys
import argparse
import pandas as pd

def main(args):
    df1 = pd.read_csv(args.CSV1, sep=args.sep, index_col=0)
    df2 = pd.read_csv(args.CSV2, sep=args.sep, index_col=0)
    out = pd.merge(df1, df2, how='outer', left_index=True, right_index=True, suffixes=('_l', '_r'), validate='one_to_one')
    out.to_csv(args.out, sep='\t', index_label='index')

if __name__ == "__main__":
    desc = ("Takes in two CSV files and merges based on a common index. The index is assumed to "
            "be the first column of each file.")
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('CSV1')
    parser.add_argument('CSV2')
    parser.add_argument('-s', '--sep')
    parser.add_argument('-o', '--out', nargs='?', default=sys.stdout, type=argparse.FileType('w'))
    args = parser.parse_args()
    for f in [args.CSV1, args.CSV2]:
        if not os.path.isfile(f):
            sys.exit("Specified file does not exist: {}".format(f))
    main(args)
