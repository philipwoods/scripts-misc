#!/home/pwoods/miniconda3/bin/python
import sys
import os.path
import argparse
import numpy as np

class Histogram(object):
    """
    Ascii histogram
    Taken from https://pyinsci.blogspot.com/2009/10/ascii-histograms.html
    Licenced under GPL
    """
    def __init__(self, data, bins=10):
        """
        Class constructor

        :Parameters:
            - `data`: array like object
        """
        self.data = data
        self.bins = bins
        self.h = np.histogram(self.data, bins=self.bins)

    def horizontal(self, height=4, character ='|'):
        """Returns a multiline string containing a
        a horizontal histogram representation of self.data
        :Parameters:
            - `height`: Height of the histogram in characters
            - `character`: Character to use
        >>> d = normal(size=1000)
        >>> h = Histogram(d,bins=25)
        >>> print h.horizontal(5,'|')
        106            |||
                      |||||
                      |||||||
                    ||||||||||
                   |||||||||||||
        -3.42                         3.09
        """
        his = """"""
        bars = self.h[0]*height/max(self.h[0])
        for l in reversed(range(1,height+1)):
            line = ""
            if l == height:
                line = '%s '%max(self.h[0]) #histogram top count
            else:
                line = ' '*(len(str(max(self.h[0])))+1) #add leading spaces
            for c in bars:
                if c >= np.ceil(l):
                    line += character
                else:
                    line += ' '
            line +='\n'
            his += line
        his += '%.2f'%self.h[1][0] + ' '*(self.bins) +'%.2f'%self.h[1][-1] + '\n'
        return his

    def vertical(self,height=20, character ='|'):
        """
        Returns a Multi-line string containing a
        a vertical histogram representation of self.data
        :Parameters:
            - `height`: Height of the histogram in characters
            - `character`: Character to use
        >>> d = normal(size=1000)
        >>> Histogram(d,bins=10)
        >>> print h.vertical(15,'*')
                              236
        -3.42:
        -2.78:
        -2.14: ***
        -1.51: *********
        -0.87: *************
        -0.23: ***************
        0.41 : ***********
        1.04 : ********
        1.68 : *
        2.32 :
        """
        his = """"""
        xl = ['%.2f'%n for n in self.h[1]]
        lxl = [len(l) for l in xl]
        bars = self.h[0]*height//max(self.h[0])
        his += ' '*(max(bars)+2+max(lxl))+'%s\n'%max(self.h[0])
        for i,c in enumerate(bars):
            line = xl[i] +' '*(max(lxl)-lxl[i])+': '+ character*c+'\n'
            his += line
        return his

def main(args):
    data = []
    if args.file:
        with open(args.file, 'r') as f:
            remaining_header = args.header
            for line in f:
                if remaining_header > 0:
                    remaining_header = remaining_header - 1
                    continue
                fields = line.split(sep=args.sep)
                data.append(float(fields[args.column-1]))
    else:
        data = [float(x) for x in args.data]
    lenrange = int(np.max(data) - np.min(data))
    h = Histogram(data, bins=30)
    print(h.vertical(120))
    print("")
    print("Min:    {: 1g}".format(np.min(data)))
    print("Max:    {: 1g}".format(np.max(data)))
    print("Mean:   {: 1g}".format(np.mean(data)))
    print("Stdev:  {: 1g}".format(np.std(data)))
    print("Median: {: 1g}".format(np.median(data)))
    print("P10:    {: 1g}".format(np.percentile(data, 10)))
    print("P25:    {: 1g}".format(np.percentile(data, 25)))
    print("P75:    {: 1g}".format(np.percentile(data, 75)))
    print("P90:    {: 1g}".format(np.percentile(data, 90)))
    print("Count:  {: 4d}".format(len(data)))

if __name__ == "__main__":
    desc = ("Takes in one-dimensional numeric data and constructs an ASCII histogram plot.")
    parser = argparse.ArgumentParser(description=desc)
    input_sources = parser.add_mutually_exclusive_group(required=True)
    input_sources.add_argument("--data", nargs='+', help="A list of numbers to construct the histogram from.")
    input_sources.add_argument("--file", help="A file containing at least one column of numeric data.")
    file_options = parser.add_argument_group(title="File options")
    file_options.add_argument("--column", type=int, default=1, help="The column of the file to construct the histogram from. Default: 1")
    file_options.add_argument("--sep", default='\t', help="The column separator in the input file. Default: TAB")
    file_options.add_argument("--header", type=int, default=0, help="The number of header lines at the top of the file. Default: 0")
    args = parser.parse_args()
    if args.file and not os.path.isfile(args.file):
        sys.exit("The specified file does not exist: {}".format(args.file))
    main(args)

