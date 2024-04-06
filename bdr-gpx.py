#!/usr/bin/env python3

import os
import os.path
import sys

import lib

def main(args):
    if not os.path.isdir('output'):
        os.makedirs('output')

    for fname in args:
        print()
        print(fname)

        basename = os.path.split(fname)[1]
        fout = f'output/{basename}'
        lib.process(fname, fout)

if __name__ == '__main__':
    main(sys.argv[1:])
