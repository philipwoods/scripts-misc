#!/bin/bash

usage() {
    echo "extract-pdf-pages.sh [-h] -f <first> -l <last> [-o <output>] -i <input>"
    echo "  Takes in a PDF and extracts the pages between the specified first"
    echo "  and last page (inclusive) into a new output PDF."
}

input=""
output=""
first=""
last=""

while getopts ':hd:o:f:l:i:' opt; do
    case $opt in
        h)  usage
            exit 1
            ;;
        d)  dir="${OPTARG}"
            ;;
        o)  output="${OPTARG}"
            ;;
        f)  first="${OPTARG}"
            ;;
        l)  last="${OPTARG}"
            ;;
        i)  input="${OPTARG}"
            ;;
        :)  echo "Invalid option: -${OPTARG} requires an argument" >&2
            exit 1
            ;;
        \?) echo "Invalid option: -${OPTARG}" >&2
            exit 1
            ;;
    esac
done

# Check required arguments
if [[ -z $input ]]; then
    echo "No input file specified." >&2
    exit 1
fi
if [[ -z $first || -z $last ]]; then
    echo "You must specify a first and last page of the range to extract."
    exit 1
fi
if [[ $last -lt $first ]]; then
    echo "The end of the extracted range cannot be earlier than the start."
    exit 1
fi

# If no output is provided...
if [[ -z $output ]]; then
    echo "No output file specified. Defaulting to ./output.pdf" >&2
    output='./output.pdf'
fi

echo "Splitting input..."
pdfseparate -f $first -l $last $input "%d-temp-page.pdf"
sorted=$(echo $(printf '%s\n' *-temp-page.pdf | sort -n))
echo "Merging output..."
pdfunite $sorted "$output"
rm -f $sorted

echo "Done!"

exit 0
