"""
The meeting one verification

Usage:
python meeting-one.py <DATA_PATH>

data path should NOT have a trailing slash
"""

from filenames import *
from data import *
import sys

DATA_PATH = sys.argv[1] or "testdata"

# get the election data
partition_file_path = file_in_dir(DATA_PATH, PARTITIONS)
election_spec_path = file_in_dir(DATA_PATH, ELECTION_SPEC)
election = parse_meeting_one_in(partition_file_path, election_spec_path, file_in_dir(DATA_PATH, MEETING_ONE_IN))

# get the p table and d tables
p_table, partitions = parse_meeting_one_out(file_in_dir(DATA_PATH, MEETING_ONE_OUT))

# check that there are as many ballots in the P table as claimed
assert len(p_table.rows) == election.num_ballots, "P Table has the wrong number of ballots, should be %s " % election.num_ballots

# loop through partitions
for p_id, partition in partitions.iteritems():
  # loop through d tables for that partition
  for d_table_id, d_table in partition.iteritems():
    # check that it has the right number of ballots
    assert len(d_table.rows) == election.num_ballots, "D Table %s in partition %s has the wrong number of ballots, should be %s" % (d_table_id, p_id, election.num_ballots)