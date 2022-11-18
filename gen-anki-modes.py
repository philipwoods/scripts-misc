#!/usr/bin/env python3
import os.path
import sys
import re
import random
import subprocess
import argparse
import pandas as pd
import mingus.core.scales as scales
from mingus.containers import Track
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
    # Normalize output directory
    out_dir = os.path.abspath(args.directory)

    ## Specify mode note fields
    flat = '\u266D'
    sharp = '\u266F'
    data = {
            '## Index':[1, 2, 3, 4, 5, 6, 7],
            'Mode':['Ionian', 'Dorian', 'Phyrgian', 'Lydian', 'Mixolydian', 'Aeolian', 'Locrian'],
            'Modifications':['none', '{0}3,{0}7'.format(flat), '{0}2,{0}3,{0}6,{0}7'.format(flat), '{0}4'.format(sharp), '{0}7'.format(flat), '{0}3,{0}6,{0}7'.format(flat), '{0}2,{0}3,{0}5,{0}6,{0}7'.format(flat)],
            'Sheet Music':[],
            'Mode Sound':[]
        }
    print("\nGenerating Anki note data...\n")
    ## List ascending and descending notes
    modes = {
            'Ionian': [],
            'Dorian': [],
            'Phrygian': [],
            'Lydian': [],
            'Mixolydian': [],
            'Aeolian': [],
            'Locrian': []
        }
    modes['Ionian'].extend(scales.Ionian("C").ascending())
    modes['Ionian'].extend(scales.Ionian("C").descending())
    modes['Dorian'].extend(scales.Dorian("C").ascending())
    modes['Dorian'].extend(scales.Dorian("C").descending())
    modes['Phrygian'].extend(scales.Phrygian("C").ascending())
    modes['Phrygian'].extend(scales.Phrygian("C").descending())
    modes['Lydian'].extend(scales.Lydian("C").ascending())
    modes['Lydian'].extend(scales.Lydian("C").descending())
    modes['Mixolydian'].extend(scales.Mixolydian("C").ascending())
    modes['Mixolydian'].extend(scales.Mixolydian("C").descending())
    modes['Aeolian'].extend(scales.Aeolian("C").ascending())
    modes['Aeolian'].extend(scales.Aeolian("C").descending())
    modes['Locrian'].extend(scales.Locrian("C").ascending())
    modes['Locrian'].extend(scales.Locrian("C").descending())
    # Specify higher octave for peak notes
    for notes in modes.values():
        notes[7] = 'C-5'
        notes[8] = 'C-5'
    for mode, notes in modes.items():
        # Generate sheet music file
        track = Track()
        for note in notes:
            track + note
        sheet_base = "mode_{0}_sheet.png".format(mode)
        sheet = os.path.join(out_dir, sheet_base)
        lilypond.to_png(lilypond.from_Track(track), sheet)
        data['Sheet Music'].append('<img src="{}">'.format(sheet_base))
        # Generate audio file names
        audio_base = "mode_{0}".format(mode)
        data['Mode Sound'].append("[sound:{}.mp3]".format(audio_base))
        mode_file = os.path.join(out_dir, "{}.wav".format(audio_base))
        # Generate audio files, 0.5 seconds per note
        fluidsynth.init(args.soundfont, file=mode_file)
        fluidsynth.play_Track(track, 1, bpm=120)
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
    desc = ("Generates a text file for importing mode training notes into Anki. "
            "Also generates the supporting image and audio files for these notes.")
    epil = ("Designed for use in bash. Requires prior installation of LilyPond, ffmpeg, and imagemagick.")
    parser = argparse.ArgumentParser(description=desc, epilog=epil)
    parser.add_argument('directory', help="A directory to place generated files into.")
    parser.add_argument('--file', default="anki-modes.txt",
            help="Name of the file containing note information to import into Anki. Default: %(default)s")
    parser.add_argument('--soundfont', default='/home/pwoods/static/soundfonts/GeneralUser_v1.471.sf2',
            help="SoundFont file used to initialize FluidSynth. Default: %(default)s")
    args = parser.parse_args()
    if not os.path.isdir(args.directory):
        sys.exit("The specified directory doesn't exist: {}".format(args.directory))
    main(args)

