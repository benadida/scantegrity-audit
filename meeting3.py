"""
The meeting three verification

Usage:
python meeting3.py <DATA_PATH>

data path should NOT have a trailing slash
"""

# core imports
import sys
import base, data, filenames

# use the meeting1 and meeting2 data structures too
import meeting1, meeting2

election, committed_p_table = meeting1.election, meeting1.p_table

# third meeting
meeting_three_in_xml = base.file_in_dir(base.DATA_PATH, filenames.MEETING_THREE_IN, 'Meeting Three In')
meeting_three_out_xml = base.file_in_dir(base.DATA_PATH, filenames.MEETING_THREE_OUT, 'Meeting Three Out')
meeting_three_out_codes_xml = base.file_in_dir(base.DATA_PATH, filenames.MEETING_THREE_OUT_CODES, 'Meeting Three Out Codes')

# parse the ballot confirmation code commitments
ballots = data.parse_ballot_table(meeting2.meeting_two_out_commitments_xml)

# get the P table of actual votes
p_table_votes = data.PTable()
p_table_votes.parse(meeting_three_in_xml.find('print'))

# get the opening of the ballot confirmation code commitments
ballots_with_codes = data.parse_ballot_table(meeting_three_out_codes_xml)

def verify(output_stream):
  # make sure none of the actual votes use ballots that were audited in Meeting2:
  assert set(p_table_votes.rows.keys()).isdisjoint(set(meeting2.challenge_row_ids))
  
  # check the openings
  for ballot_open in ballots_with_codes.values():
    ballot = ballots[ballot_open.pid]
    assert ballot.verify_code_openings(ballot_open, election.constant)

    # check that the coded votes correspond to the confirmation code openings
    assert ballot_open.verify_encodings(election, p_table_votes)
    
  # we get the half-decrypted votes, but there's nothing to verify yet
  
  # we get the R table, and that can be tallied based on the type of question
  # however, just to separate the cryptographic verification from the actual
  # counting, which should be a lot simpler, the counting of the R table is done
  # in the tally.py program.
  
  output_stream.write("""Election ID: %s
Meeting 3 Successful

%s ballots cast

The tally can now be computed, not fully verified yet, using tally.py

%s
""" % (election.spec.id, len(ballots_with_codes), base.fingerprint_report()))

if __name__ == '__main__':
  verify(sys.stdout)