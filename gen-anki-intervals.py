#!/usr/bin/env python3
import os.path
import sys
import re
import random
import subprocess
import argparse
import pandas as pd
import mingus.core.keys as keys
import mingus.core.intervals as intervals
from mingus.containers import Note
from mingus.containers import Bar
from mingus.midi import fluidsynth
from mingus.extra import lilypond

##### IMPORTANT INFO ABOUT MINGUS #####
#
# In order for this to work properly, I had to modify a few
# files in the mingus package. If you have to reinstall or
# update the environment, you will need to change these things:
#
# mingus/midi/fluidsynth.py:
# Change line 126 from:
#   if not initialized:
# to:
#   if initialized or not initialized:
#
# mingus/extras/lilypond.py:
# Change line 252 from:
#   command = 'lilypond %s -o "%s" "%s.ly"' % (command, filename, filename)
# to:
#   command = 'lilypond -dresolution=200 %s -o "%s" "%s.ly"' % (command, filename, filename)
#
#######################################

def main(args):
    # Configure the intervals to generate. Each dictionary
    # key is the name of the interval. The first field is
    # the shorthand name, and the second field is the number
    # of Anki notes to generate for that interval.
    interval_config = {
                'perfect octave': ('1', 2),
                'minor second': ('b2', 2),
                'major second': ('2', 2),
                'minor third': ('b3', 2),
                'major third': ('3', 2),
                'perfect fourth': ('4', 2),
                'tritone (augmented fourth)': ('#4', 1),
                'tritone (diminished fifth)': ('b5', 1),
                'perfect fifth': ('5', 2),
                'minor sixth': ('b6', 2),
                'major sixth': ('6', 2),
                'minor seventh': ('b7', 2),
                'major seventh': ('7', 2),
            }
    # Allow savvy users to ask for rerolls of specific intervals.
    # Best used in conjunction with the --index option.
    if args.config is not None:
        interval_config = {args.config[0]: (args.config[1], int(args.config[2]))}
    # Specify the deck size modifier
    # (Anki notes = count field * size modifier)
    size_modifier = 2
    if args.size == 'short':
        size_modifier = 1
    if args.size == 'long':
        size_modifier = 4
    if args.config is not None:
        size_modifier = 1
    # Specify interval directions
    directions = []
    if args.direction in ['ascending', 'both']:
        directions.append('ascending')
    if args.direction in ['descending', 'both']:
        directions.append('descending')
    # Normalize output directory
    out_dir = os.path.abspath(args.directory)

    ## Start Anki note generation
    data = {
            '## Index':[],
            'Key':[],
            'Start Note':[],
            'End Note':[],
            'Direction':[],
            'Interval':[],
            'Sheet Music':[],
            'Start Sound':[],
            'End Sound':[],
            'Interval Sound':[]
        }
    index = args.index
    print("\nGenerating Anki note data...\n")
    for interval, (shorthand, count) in interval_config.items():
        for direction in directions:
            for i in range(count*size_modifier):
                data['## Index'].append(index)
                # Generate initial basic fields
                accidentals = round(random.triangular(-7,7,0)) 
                key = keys.get_key(accidentals)[0] # Pick random major key, weighted towards 'typical' keys
                start = random.choice(keys.get_notes(key)) # Pick random note from our key
                end = intervals.from_shorthand(start, shorthand, direction=='ascending')
                data['Key'].append(key)
                data['Start Note'].append(start)
                data['End Note'].append(end)
                data['Direction'].append(direction)
                data['Interval'].append(interval)
                # Generate sheet music file
                interval_bar = Bar(key)
                start_note = Note(start)
                end_note = Note(start)
                end_note.transpose(shorthand, direction=='ascending')
                if shorthand == '1':
                    if direction == 'ascending':
                        end_note.octave_up()
                    if direction == 'descending':
                        end_note.octave_down()
                interval_bar.place_notes(start_note, 2)
                interval_bar.place_notes(end_note, 2)
                sheet_base = "interval_{0}_sheet.png".format(index)
                sheet = os.path.join(out_dir, sheet_base)
                lilypond.to_png(lilypond.from_Bar(interval_bar), sheet)
                data['Sheet Music'].append('<img src="{}">'.format(sheet_base))
                # Generate audio file names
                start_base = "interval_{0}_start".format(index)
                end_base = "interval_{0}_end".format(index)
                interval_base = "interval_{0}_full".format(index)
                data['Start Sound'].append("[sound:{}.mp3]".format(start_base))
                data['End Sound'].append("[sound:{}.mp3]".format(end_base))
                data['Interval Sound'].append("[sound:{}.mp3]".format(interval_base))
                start_file = os.path.join(out_dir, "{}.wav".format(start_base))
                end_file = os.path.join(out_dir, "{}.wav".format(end_base))
                interval_file = os.path.join(out_dir, "{}.wav".format(interval_base))
                # Generate audio files, 2 seconds per note
                start_bar = Bar(key)
                start_bar.place_notes(start_note, 1)
                end_bar = Bar(key)
                end_bar.place_notes(end_note, 1)
                fluidsynth.init(args.soundfont, file=start_file)
                fluidsynth.play_Bar(start_bar, 1, bpm=120)
                fluidsynth.init(args.soundfont, file=end_file)
                fluidsynth.play_Bar(end_bar, 1, bpm=120)
                fluidsynth.init(args.soundfont, file=interval_file)
                fluidsynth.play_Bar(interval_bar, 1, bpm=60)
                # Increment Anki note index
                index += 1
                print("\n")
    ## Create text file for Anki note importing
    df = pd.DataFrame(data)
    out_file = os.path.join(out_dir, args.file)
    df.to_csv(out_file, sep=';', index=False, quotechar="'")

    ## Final adjustments with bash tools
    # Anki requires fields to be delimited by '; ' not just ';'
    subprocess.run(['sed', '-i', 's/;/; /g', out_file], cwd=out_dir)
    # LilyPond PNG output is one whole page (835x1181px) with footer text
    # We can crop off the bottom of the page to remove the footer,
    # then use the -trim option to remove extra whitespace.
    print("Cropping sheet music images...\n")
    subprocess.run("for f in *.png; do mogrify -crop 835x800+0+0 $f; done", shell=True, cwd=out_dir)
    subprocess.run("for f in *.png; do mogrify -trim $f; done", shell=True, cwd=out_dir)
    # Convert the FluidSynth output .wav files to .mp3
    print("Converting audio files to MP3...\n")
    subprocess.run("for f in *.wav; do ffmpeg -hide_banner -loglevel warning -i $f -vn -y ${f%.wav}.mp3; done", shell=True, cwd=out_dir)
    subprocess.run("rm -f *.wav", shell=True, cwd=out_dir)
    print("Done! Output in the directory {}".format(args.directory))

if __name__ == "__main__":
    desc = ("Generates a text file for importing interval training notes into Anki. "
            "Also generates the supporting image and audio files for these notes.")
    epil = ("Designed for use in bash. Requires prior installation of LilyPond, ffmpeg, and imagemagick.")
    parser = argparse.ArgumentParser(description=desc, epilog=epil)
    parser.add_argument('directory', help="A directory to place generated files into.")
    parser.add_argument('--file', default="anki-intervals.txt",
            help="Name of the file containing note information to import into Anki. Default: %(default)s")
    parser.add_argument('--direction', choices=['ascending', 'descending', 'both'], default='both',
            help="Specifies the direction of intervals to generate. Default: %(default)s")
    parser.add_argument('--size', choices=['default', 'short', 'long'], default='default',
            help="Size of the deck to create. Modifies the number of examples per interval. Default: %(default)s")
    parser.add_argument('--soundfont', default='/home/pwoods/static/soundfonts/GeneralUser_v1.471.sf2',
            help="SoundFont file used to initialize FluidSynth. Default: %(default)s")
    parser.add_argument('--index', default=0, type=int, help="Choose a starting index. Don't use unless you know what you're doing.")
    parser.add_argument('--config', default=None, nargs=3, help="Set configuration information. Don't use unless you know what you're doing.")
    args = parser.parse_args()
    if not os.path.isdir(args.directory):
        sys.exit("The specified directory doesn't exist: {}".format(args.directory))
    main(args)

