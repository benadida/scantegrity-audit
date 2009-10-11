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
meeting_one_in_path = file_in_dir(DATA_PATH, MEETING_ONE_IN)
meeting_one_out_path = file_in_dir(DATA_PATH, MEETING_ONE_OUT)

election = parse_meeting_one_in(partition_file_path, election_spec_path, meeting_one_in_path)

# get the p table and d tables
p_table, partitions = parse_meeting_one_out(meeting_one_out_path)

# check that there are as many ballots in the P table as claimed
assert len(p_table.rows) == election.num_ballots, "P Table has the wrong number of ballots, should be %s " % election.num_ballots

# loop through partitions
for p_id, partition in partitions.iteritems():
  # loop through d tables for that partition
  for d_table_id, d_table in partition.iteritems():
    # check that it has the right number of ballots
    assert len(d_table.rows) == election.num_ballots, "D Table %s in partition %s has the wrong number of ballots, should be %s" % (d_table_id, p_id, election.num_ballots)
    
print """Election ID: %s
Meeting 1 Successful

- Partition File: %s
- Election Spec: %s
- Meeting One In: %s
- Meeting One Out: %s

""" % (election.spec.id, hash_file(partition_file_path), hash_file(election_spec_path), hash_file(meeting_one_in_path), hash_file(meeting_one_out_path))