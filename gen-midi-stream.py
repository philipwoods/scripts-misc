#!/usr/bin/env python3
import os
import sys
import re
import argparse
import pandas as pd
import music21

def format_pitch(pitch_string):
    pattern = "([AaBbCcDdEeFfGg])([#b]?)-?(\d)"
    result = re.fullmatch(pattern, pitch_string)
    if result is None:
        sys.exit("The input pitch string format is invalid: {}".format(pitch_string))
    accidental = ""
    if result.group(2) == "#":
        accidental = "#"
    if result.group(2) == "b":
        accidental = "-"
    output = result.group(1).upper() + accidental + result.group(3)
    return output

def main(args):
    notes_list = pd.read_csv(args.input, sep='\t', index_col=False, header=0, names=['pitch', 'beat_count'])
    sequence = music21.stream.Stream()
    for row in notes_list.itertuples():
        pitch_string = format_pitch(row.pitch)
        note = music21.note.Note(pitch_string, quarterLength=row.beat_count)
        sequence.append(note)
    sequence.write(fmt=args.format, fp=args.output)

if __name__ == "__main__":
    desc = ("Takes in an input TSV describing a sequence of pitches and writes a corresponding MIDI stream to an output file."
            "The input TSV must contain two columns: pitch and beat_count")
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-i', '--input', required=True,
            help="Input file. Must contain two columns describing the note stream (pitch and beat_count)")
    parser.add_argument('-o', '--output', required=True,
            help="Path to write output midi stream as a file.")
    parser.add_argument('--format', default='musicxml', choices=['musicxml', 'midi', 'lilypond'],
            help="Set output format. Default: %(default)s")
    args = parser.parse_args()
    if not os.path.isfile(args.input):
        sys.exit("Invalid input file: {}".format(args.input))
    main(args)

