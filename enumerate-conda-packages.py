#!/usr/bin/env python
import os
import sys
import json
import argparse
import pandas as pd
import subprocess as sp

# Is there a decent way to check for manually installed packages like the prot_loc one on ocean?
# Maybe compare this output to a list of the things in $CONDA_PREFIX/bin?

def main(args):
    # Get list of env prefixes
    env_json = sp.run(['conda', 'info', '--envs', '--json'], capture_output=True, text=True).stdout
    env_prefixes = json.loads(env_json)['envs']
    output_records = []
    for prefix in env_prefixes:
        # Get env name from env prefix
        if prefix.count('env') == 0:
            env_name = "base"
        else:
            env_name = os.path.basename(prefix)
        # Get package info
        pkg_json = sp.run(['conda', 'list', '--json', '-p', prefix], capture_output=True, text=True).stdout
        pkgs_obj = json.loads(pkg_json)
        for pkg in pkgs_obj:
            record = {
                    'package': pkg['name'],
                    'version': pkg['version'],
                    'env': env_name,
                    'channel': pkg['channel']
                    }
            output_records.append(record)
    # Create DataFrame for output formatting
    out = pd.DataFrame.from_records(output_records)
    out.sort_values(by=['package', 'env'], inplace=True)
    out.to_csv(args.output, sep='\t', index=False)
    if args.excel:
        out.to_excel(args.excel, index=False, freeze_panes=(1,0), autofilter=True)

def main_original(args):
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
    out.sort_values('package', inplace=True)
    out.to_csv(args.output, sep='\t', index=False)
    if args.excel:
        out.to_excel(args.excel, index=False, freeze_panes=(1,0), autofilter=True)

if __name__ == "__main__":
    desc = ("List basic information about all conda environments on the "
            "system and the packages installed in those environments.")
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-o', '--output', default='output.tsv', help="Output file destination. Default: %(default)s")
    parser.add_argument('--excel', help="Additional optional file output in XLSX format.")
    args = parser.parse_args()
    main(args)
