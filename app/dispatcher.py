from __future__ import print_function
from itertools import *

import os
import re
import sys

import runner


def get_files(folder, pattern):
    return (os.path.abspath(os.path.join(dirpath, filename))
            for (dirpath, dirnames, filenames) in os.walk(folder)
            for filename in filenames
            if re.search(pattern, filename))

def dispatch(filepath):
    with open(filepath, 'r') as f:
        return runner.run.delay(filepath, f.read())


if len(sys.argv) < 2:
    print('Usage: dispatcher.py <folder1> [folder2 ... folderN]')
    sys.exit(1)

results = list(map(dispatch, chain.from_iterable(get_files(f, '.py$') for f in sys.argv[1:])))

list(map(print, results))
