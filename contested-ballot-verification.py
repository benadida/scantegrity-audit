"""
The contested ballot verification

Usage:
python contested-ballot-verification.py <DATA_PATH>

data path should NOT have a trailing slash
"""

# based on meeting2, no need to check against meeting3 and meeting4
from meeting2 import *

# contested ballots reveal
contested_ballots_reply_xml = file_in_dir(DATA_PATH, CONTESTED_BALLOTS_REPLY, 'Reply to Contested Ballots')
contested_ballots = parse_ballot_table(contested_ballots_reply_xml)

if __name__ == '__main__':
  # go through the contested ballots
  print """Election ID: %s
Contested Ballots Audit Successful

%s
""" % (election.spec.id, fingerprint_report())