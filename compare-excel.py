#!/usr/bin/env python
import os
import sys
import numpy as np
import pandas as pd
import argparse

def main(args):
    template_sheets = pd.read_excel(args.template, sheet_name=None, header=None)
    test_sheets = pd.read_excel(args.test, sheet_name=None, header=None)

    template_keys = template_sheets.keys()
    test_keys = test_sheets.keys()

    print("="*40)
    print("Comparing sheet names")
    print("-"*40)
    if set(template_keys) != set(test_keys):
        err = """
        Mismatched sheet names:
        Template: {0}
        Test:     {1}
        """. format(",".join(list(template_keys)), ",".join(list(test_keys)))
        sys.exit(err)
    else:
        print("Sheet names match.")
    print("="*40)

    for sheet in template_keys:
        print("="*40)
        print("Comparing sheet '{}'".format(sheet))
        print("-"*40)
        template_df = template_sheets[sheet]
        test_df = test_sheets[sheet]
        difference_df = pd.DataFrame(columns=["Row", "Column", "Template", "Test"])
        # Iterate through cells in the sheet
        rtemplate,ctemplate = template_df.shape
        rtest,ctest = test_df.shape
        for row in range(max(rtemplate, rtest)):
            for col in range(max(ctemplate, ctest)):
                # Get cell value in template
                try:
                    template_val = template_df.iloc[row,col]
                except:
                    template_val = np.nan
                # Get cell value in test
                try:
                    test_val = test_df.iloc[row,col]
                except:
                    test_val = np.nan
                # Compare the cell values
                if str(template_val) != str(test_val):
                    tmp_df = pd.DataFrame([[row, col, template_val, test_val]], columns=["Row", "Column", "Template", "Test"])
                    difference_df = pd.concat([difference_df, tmp_df], ignore_index=True)
        if difference_df.empty:
            print("NO DIFFERENCE IN DATA")
        else:
            print(difference_df.to_string(index=False))
        print("="*40)

if __name__ == "__main__":
    desc = ("Compares two Excel documents to identify differences in cell values. Works "
            "best when the documents are highly similar. The output shows a table of the "
            "cell value differences between the test and template documents. NaN may "
            "indicate an empty cell in that sheet.")
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("template", help="Template Excel document to test against.")
    parser.add_argument("test", help="Document which may or may not be equal to the template.")
    args = parser.parse_args()
    main(args)
