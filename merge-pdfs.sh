#!/bin/bash

usage() {
    echo "merge-pdfs.sh [-h] [-d <input-dir>] -o <output> <in-1> <in-2> ... <in-n>"
    echo "  Takes in an output file specified with the -o option and a set of input"
    echo "  PDF files, which will be concatenated in the order they are provided."
    echo "  The -d option can be used to specify a directory containing input files."
    echo "  If this option is provided, positional arguments will be ignored."
}

dir=""
output=""

while getopts ':hd:o:' opt; do
    case $opt in
        h)  usage
            exit 1
            ;;
        d)  dir="${OPTARG}"
            ;;
        o)  output="${OPTARG}"
            ;;
        :)  echo "Invalid option: -${OPTARG} requires an argument" >&2
            exit 1
            ;;
        \?) echo "Invalid option: -${OPTARG}" >&2
            exit 1
            ;;
    esac
done

# If no output is provided...
if [[ -z $output ]]; then
    echo "No output file specified. Defaulting to ./output.pdf" >&2
    output='./output.pdf'
fi
# If a directory was provided...
if [[ -n $dir ]]; then
    # Check if the directory exists
    if [[ ! -d $dir ]]; then
        echo "Directory does not exist: $dir" >&2
        exit 1
    fi
    # If it does, list the pdfs in the directory
    inputs=$(echo $dir/*.pdf | sed "s/\/\//\//g")
else
    # If no directory was provided, get the remaining positional args
    shift $((OPTIND -1))
    inputs="$@"
fi

num=$(wc -w <<< $inputs)
echo "Merging $num files into $output:"
sed "s/ /\n/g" <<< $inputs
pdfunite $inputs "$output"
echo "Done!"

exit 0
