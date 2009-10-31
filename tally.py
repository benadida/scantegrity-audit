"""
The tallying of the R tables, no verification otherwise

Usage:
python tally.py <DATA_PATH>

data path should NOT have a trailing slash
"""

# core imports
import sys
import base, data, filenames

# use the meeting1 and meeting2 data structures too
import meeting1, meeting4

election = meeting1.election
r_tables = meeting4.r_tables_by_partition

import pdb; pdb.set_trace()

def tally(output_stream):
  
  output_stream.write("""Election ID: %s
Tally

%s ballots cast

""" % (election.spec.id, len(ballots_with_codes)))

if __name__ == '__main__':
  tally(sys.stdout)