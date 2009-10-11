"""
The meeting two verification

Usage:
python meeting2.py <DATA_PATH>

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

# second meeting
meeting_two_in_path = file_in_dir(DATA_PATH, MEETING_TWO_IN)
meeting_two_out_path = file_in_dir(DATA_PATH, MEETING_TWO_OUT)

# get the challenges
challenge_p_table = parse_meeting_two_in(meeting_two_in_path)

# get the response
response_p_table, response_partitions = parse_meeting_two_out(meeting_two_out_path)

challenge_row_ids = challenge_p_table.rows.keys()

p_table_permutations = {}

# check the P table commitments
for row_id in challenge_row_ids:
  assert p_table.check_full_row(response_p_table.rows[row_id], election.constant), "commitment doesn't match in P table"

# Now we go through the partitions, the d tables within each partition,
# and we look at the rows that are revealed. As we do this, we'll also
# spot check that the permutations in a given d_table row match the p_table permutations
# for that question.

# first we get the partition-and-question map for this election, which
# is effectively a tree representation of how the questions are grouped
# in partitions, with each leaf being the number of answers for that given question.
partition_map = election.partition_map

# loop through partitions
for p_id, partition in partitions.iteritems():
  # loop through d tables for that partition
  for d_table_id, d_table in partition.iteritems():
    # get the corresponding response D table
    response_d_table = response_partitions[p_id][d_table_id]
    
    # for efficiency of lookup, so we don't have to look up D-table rows by p-table row ID
    # (which we haven't indexed), we check that
    # (1) the responses are correct according to the commitments
    # (2) the list of p_id rows in each response set matches the challenge row IDs
    
    # (1) reveals match
    for row_id, response_row in response_d_table.rows.iteritems():
      assert d_table.check_full_row(p_id, d_table_id, response_row, election.constant), "bad d table commitment"
      print "done %s %s %s" % (p_id, d_table_id, row_id)
    
    # (2) list of p_ids matches
    assert sorted(challenge_row_ids) == sorted([r['pid'] for r in response_d_table.rows.values()])
    
    # (3) permutations
    for row_id, response_row in respond_d_table.rows.iteritems():
      d_perm_left, d_perm_right = d_table.get_permutations_by_row_id(row_id)
      
      # get the corresponding P table permutation subset
      
      # compare the composition
    
##
## check that the composition of the P table permutations is the same as the composition of corresponding D tables
##
    
print """Election ID: %s
Meeting 2 Successful

- Partition File: %s
- Election Spec: %s
- Meeting One In: %s
- Meeting One Out: %s
- Meeting Two In: %s
- Meeting Two Out: %s

""" % (election.spec.id, hash_file(partition_file_path), hash_file(election_spec_path), hash_file(meeting_one_in_path),
      hash_file(meeting_one_out_path), hash_file(meeting_two_in_path), hash_file(meeting_two_out_path))