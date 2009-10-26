"""
The meeting three verification

Usage:
python meeting3.py <DATA_PATH>

data path should NOT have a trailing slash
"""

from meeting2 import *

# third meeting
meeting_three_in_xml = file_in_dir(DATA_PATH, MEETING_THREE_IN, 'Meeting Three In')
meeting_three_out_xml = file_in_dir(DATA_PATH, MEETING_THREE_OUT, 'Meeting Three Out')
meeting_three_out_codes_xml = file_in_dir(DATA_PATH, MEETING_THREE_OUT_CODES, 'Meeting Three Out Codes')

# parse the ballot confirmation code commitments
ballots = parse_ballot_table(meeting_two_out_commitments_xml)

# get the P table of actual votes
p_table_votes = PTable()
p_table_votes.parse(meeting_three_in_xml.find('print'))

# get the opening of the ballot confirmation code commitments
ballots_with_codes = parse_ballot_table(meeting_three_out_codes_xml)

if __name__ == '__main__':
  # make sure none of the actual votes use ballots that were audited in Meeting2:
  assert set(p_table_votes.rows.keys()).isdisjoint(set(challenge_row_ids))
  
  # check the openings
  for ballot_open in ballots_with_codes.values():
    ballot = ballots[ballot_open.pid]
    assert ballot.verify_code_openings(ballot_open, election.constant)
    
  # we get the half-decrypted votes, but there's nothing to verify yet
  
  # we get the R table, and that can be tallied based on the type of question
  # however, just to separate the cryptographic verification from the actual
  # counting, which should be a lot simpler, the counting of the R table is done
  # in the tally.py program.
  
  print """Election ID: %s
Meeting 3 Successful

%s ballots cast

The tally can now be computed, not fully verified yet, using tally.py

%s
""" % (election.spec.id, len(ballots_with_codes), fingerprint_report())