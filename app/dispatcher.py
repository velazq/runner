from __future__ import print_function

import os
import sys

import runner


if len(sys.argv) < 2:
    print('Usage: dispatcher.py <folder_path>')
    sys.exit(1)

def dispatch(dirpath_filename):
    path = os.path.abspath(os.path.join(*dirpath_filename))
    with open(path) as f:
        return runner.run_and_shutdown_worker.delay(path, f.read())

(dirpath, dirnames, filenames) = next(os.walk(sys.argv[1]))

results = map(dispatch, [(dirpath, filename) for filename in filenames])

for result in results:
    print(result.get())
