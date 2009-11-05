"""
Run Tally with Provisional Ballots Added

2009-11-05

Usage
python tally-provisional.py <QUESTION_ID> <DATA_PATH> <DATA_PATH_2> <DATA_PATH_3> ... 

QUESTION_ID is the question_id from electionspec.xml
data paths should NOT have a trailing slash

More than one data path because we are tallying up multiple wards at the same time

The reason for specifying the question_num is that some questions are split among multiple wards, others not.
"""

import filenames
filenames.go_provisional()

from tally import *

if __name__ == '__main__':
  tally(sys.stdout)