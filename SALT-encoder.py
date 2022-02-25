import sys
import re
import csv
import os.path

SALT_CHARS = """ !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"""

def main(args):
    helpstring = """
    Takes one argument: a text file of human-readable output from https://burnysc2.github.io/sc2-planner/
    Takes two options: -a <author> and -d <description>
    Build order name is taken from the input file name.
    Outputs a SALT string containing the specified build order to stdout.
    SALT documentation found at https://drive.google.com/file/d/0Bzrw_bC8iBjfSzFRRGlWWnNWNDg/view
    Last updated 15 August 2020
    """
    # Handle arguments
    if "-h" in args or "--help" in args:
        print(helpstring)
        sys.exit(1)
    # Allow optional flags -a and -d for specifying author and description
    author = ""
    desc = ""
    while len(args) > 0 and args[0][0] == "-":
        arg = args.pop(0)
        if arg == "-a":
            author = args.pop(0)
        elif arg == "-d":
            desc = args.pop(0)
    if len(args) != 1:
        print("This script requires exactly one positional input. Use the --help option for more information.")
        sys.exit(1)
    filename = args.pop(0)

    # Build name taken from file name
    build = filename.split(".")[0].strip().replace(" ","_")
    SALT_string = "%{build}|{author}|{description}|~".format(build=build, author=author, description=desc)
    # Format is "MM:SS SUPPLY ACTION"
    pattern = re.compile("(\d\d):(\d\d) (\d+) (.+)")

    with open(filename, 'r') as f:
        for line in f:
            match = pattern.match(line)
            mins, secs, supply, action = match.groups()
            # Several BurnySC events don't have SALT counterparts
            if "MULE" in action or "3x Mine gas" in action or "Lift" in action or "to free" in action:
                continue
            mins = encodeNumber(int(mins))
            secs = encodeNumber(int(secs))
            supply = encodeSupply(int(supply))
            eventType = None
            itemID = None
            # Get path to data file
            salt_map = "/home/pwoods/static/salt_map.tsv"
            with open(salt_map, 'r') as salt_table:
                reader = csv.DictReader(salt_table, delimiter='\t')
                # Format of the table file is type, item_id, salt_name, burny_name
                for row in reader:
                    # Burny specifies upgrades as (.*)Level\d but we only want to match with \1
                    if row['burny_name'].startswith(action.strip().split("Level")[0]):
                        eventType = encodeNumber(int(row['type']))
                        itemID = encodeNumber(int(row['item_id']))
            SALT_event = "{supply}{minutes}{seconds}{typeid}{itemid}".format(supply=supply, minutes=mins, seconds=secs, typeid=eventType, itemid=itemID)
            SALT_string += SALT_event
    # Finished constructing the string
    print(SALT_string)

def encodeNumber(i):
    if i >= len(SALT_CHARS):
        return SALT_CHARS[0]
    else:
        return SALT_CHARS[i]

def encodeSupply(supply):
    if supply < 11 or (supply - 10) > len(SALT_CHARS):
        return SALT_CHARS[0]
    else:
        return SALT_CHARS[supply-10]

if __name__=="__main__":
    main(sys.argv[1:])

