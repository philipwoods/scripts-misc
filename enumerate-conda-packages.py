#!/usr/bin/env python
import os
import sys
import json
import argparse
import pandas as pd
import subprocess as sp

# Currently only lists conda-installed packages, not pip-installed packages
# May need two steps:
# 1. List env paths with conda info --envs --json
#    The relevant output will be results_obj['envs'], which is a list of conda prefix paths
# 2. Iterate through envs and do conda list -p <env-path> --json
#    To get relevant data, [(package['name'], package['version'], package['channel']) for package in results_obj]
# Then do final compilation and formatting

def main(args):
    results_json = sp.run(['conda', 'search', '--envs', '--json'], capture_output=True, text=True).stdout
    results_obj = json.loads(results_json)
    output_records = []
    for env_data in results_obj:
        # Get the path to the environment and extract the env name
        conda_prefix = env_data['location']
        if conda_prefix.count('env') == 0:
            env_name = "base"
        else:
            env_name = os.path.basename(conda_prefix)
        # Extract package names and versions from the data
        packages = env_data['package_records']
        for package in packages:
            package_name = package['name']
            package_version = package['version']
            record = {
                    "package": package_name,
                    "version": package_version,
                    "env": env_name
                    }
            output_records.append(record)
    out = pd.DataFrame.from_records(output_records)
    out.to_csv(args.output, sep='\t', index=False)

if __name__ == "__main__":
    desc = ("List basic information about all conda environments on the "
            "system and the packages installed in those environments.")
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-o', '--output', default='output.tsv', help="Output file destination. Default: %(default)s")
    args = parser.parse_args()
    main(args)
