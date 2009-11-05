"""
Run Meeting 3 with Provisional Ballots Added

2009-11-05

Usage:
python meeting3-provisional.py <DATA_PATH> [<CODES_FILE_PATH>]

data path should NOT have a trailing slash

CODES_FILE_PATH is the path to a file which, when provided, will be where
this script writes its list of confirmation codes for each ballot.
"""

import filenames
filenames.go_provisional()

from meeting3 import *

if __name__ == '__main__':
  if len(sys.argv) > 2:
    codes_output = open(sys.argv[2], "w")
  else:
    codes_output = None
  verify(sys.stdout, codes_output)
  
  if codes_output:
    codes_output.close()
