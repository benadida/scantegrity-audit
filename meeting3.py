"""
The meeting three verification

Usage:
python meeting3.py <DATA_PATH> [<CODES_FILE_PATH>]

data path should NOT have a trailing slash

CODES_FILE_PATH is the path to a file which, when provided, will be where
this script writes its list of confirmation codes for each ballot.
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

def verify(output_stream, codes_output_stream=None):
  # make sure none of the actual votes use ballots that were audited in Meeting2:
  assert set(p_table_votes.rows.keys()).isdisjoint(set(meeting2.challenge_row_ids))

  if codes_output_stream:
    BALLOTS = {}
    def new_code(webSerial, pid, q_id, s_id, confirmation_code):
      if not BALLOTS.has_key(webSerial):
        BALLOTS[webSerial] = {'pid': pid, 'questions': {}}
        
      if not BALLOTS[webSerial]['questions'].has_key(q_id):
        BALLOTS[webSerial]['questions'][q_id] = []
      
      BALLOTS[webSerial]['questions'][q_id].append(confirmation_code)
  else:
    new_code = None
  
  # check the openings
  for ballot_open in ballots_with_codes.values():
    ballot = ballots[ballot_open.pid]
    assert ballot.verify_code_openings(ballot_open, election.constant, code_callback_func = new_code)

    # check that the coded votes correspond to the confirmation code openings
    assert ballot_open.verify_encodings(election, p_table_votes)
    
  # we get the half-decrypted votes, but there's nothing to verify yet
  
  # we write out the codes
  if new_code:
    codes_output_stream.write('Serial #,P-table ID')
    for q_id in sorted(BALLOTS.values()[0]['questions'].keys()):
      codes_output_stream.write(",question %s"%q_id)
    codes_output_stream.write("\n")
    
    for serial in sorted(BALLOTS.keys()):
      codes_output_stream.write('%s,%s' % (serial, BALLOTS[serial]['pid']))
      for q_id in sorted(BALLOTS[serial]['questions'].keys()):
        codes_output_stream.write(',"%s"' % ",".join(BALLOTS[serial]['questions'][q_id]))
      codes_output_stream.write("\n")
    
  
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
  if len(sys.argv) > 2:
    codes_output = open(sys.argv[2], "w")
  else:
    codes_output = None
  verify(sys.stdout, codes_output)
  
  if codes_output:
    codes_output.close()