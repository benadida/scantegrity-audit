"""
The contested ballot verification

Usage:
python contested-ballot-verification.py <DATA_PATH> [<CODES_FILE_PATH>]

data path should NOT have a trailing slash

The codes_file_path is where the contested codes should be written
"""

# core imports
import sys
import base, data, filenames

# based on meeting2, and meeting3 for the ballots which aren't needed for parsing until then, nothing in meeting4 needed
import meeting1, meeting2

# use provisional ballots
try:
  import meeting3provisional as meeting3
except:
  filenames.reset()
  import meeting3

election = meeting1.election
ballots, cast_ballots = meeting3.ballots, meeting3.ballots_with_codes

# contested ballots reveal
contested_ballots_reply_xml = base.file_in_dir(base.DATA_PATH, filenames.CONTESTED_BALLOTS_REPLY, 'Reply to Contested Ballots')
contested_ballots = data.parse_ballot_table(contested_ballots_reply_xml)

def verify(output_stream, codes_output_stream=None):
  
  if codes_output_stream:
    codes_output_stream.write('Serial #,P-table ID')
    for q_id in sorted(contested_ballots.values()[0].questions.keys()):
      codes_output_stream.write(",question %s"%q_id)
    codes_output_stream.write("\n")    

  # for each contested ballot:
  for contested_ballot in contested_ballots.values():
    # is it a cast ballot?
    assert cast_ballots.has_key(contested_ballot.pid)
    
    # does it verify against the original ballots
    assert ballots[contested_ballot.pid].verify_code_openings(contested_ballot, election.constant)
    
    if codes_output_stream:
      codes_output_stream.write('%s,%s' % (contested_ballot.webSerial, contested_ballot.pid))
      for q_id in sorted(contested_ballot.questions.keys()):
        codes_output_stream.write(',"%s"' % ",".join([q['code'] for q in contested_ballot.questions[q_id].values()]))
      codes_output_stream.write("\n")
    
  # go through the contested ballots
  output_stream.write("""Election ID: %s
Contested Ballots Audit Successful

%s ballots contested and opened successfully

%s
""" % (election.spec.id, len(contested_ballots.keys()), base.fingerprint_report()))

if __name__ == '__main__':
  if len(sys.argv) > 2:
    codes_output = open(sys.argv[2], "w")
  else:
    codes_output = None
    
  verify(sys.stdout, codes_output)
  
  if codes_output:
    codes_output.close()