from __future__ import print_function
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


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: dispatcher.py <folder1> [folder2 ... folderN]')
        sys.exit(1)

    results = [dispatch(f) for d in sys.argv[1:] for f in get_files(d, '.py$')]

    [print(r.get()) for r in results]
