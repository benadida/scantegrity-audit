"""
The meeting three verification

Usage:
python meeting3.py <DATA_PATH>

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
meeting_two_out_commitments_path = file_in_dir(DATA_PATH, MEETING_TWO_OUT_COMMITMENTS)

# get the challenges
challenge_p_table = parse_meeting_two_in(meeting_two_in_path)

# get the response
response_p_table, response_partitions = parse_meeting_two_out(meeting_two_out_path)

challenge_row_ids = challenge_p_table.rows.keys()

##
## UP TO HERE, same as MEETING TWO
##

# third meeting
meeting_three_in_path = file_in_dir(DATA_PATH, MEETING_THREE_IN)
meeting_three_out_path = file_in_dir(DATA_PATH, MEETING_THREE_OUT)
meeting_three_out_codes_path = file_in_dir(DATA_PATH, MEETING_THREE_OUT_CODES)

# parse the ballot confirmation code commitments
ballots = parse_meeting_two_out_commitments(meeting_two_out_commitments_path)

# get the P table of actual votes
p_table_votes = parse_meeting_three_in(meeting_three_in_path)

# get the opening of the ballot confirmation code commitments
ballots_with_codes = parse_meeting_three_out_codes(meeting_three_out_codes_path)

# check the openings
for ballot_open in ballots_with_codes.values():
  ballot = ballots[ballot_open.pid]
  assert ballot.verify_code_openings(ballot_open, election.constant)
  
##
## check that the composition of the P table permutations is the same as the composition of corresponding D tables
##
    
print """Election ID: %s
Meeting 3 Successful

%s ballots cast

FINGERPRINTS
- Partition File: %s
- Election Spec: %s
- Meeting One In: %s
- Meeting One Out: %s
- Meeting Two In: %s
- Meeting Two Out: %s
- Meeting Three In: %s
- Meeting Three Out: %s

""" % (election.spec.id, len(ballots_with_codes), hash_file(partition_file_path), hash_file(election_spec_path), hash_file(meeting_one_in_path),
      hash_file(meeting_one_out_path), hash_file(meeting_two_in_path), hash_file(meeting_two_out_path),
      hash_file(meeting_three_in_path), hash_file(meeting_three_out_path))