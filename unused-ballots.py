"""
The unused ballot verification

Usage:
python unused-ballot-verification.py <DATA_PATH> [<CODES_FILE_PATH>]

data path should NOT have a trailing slash

CODES_FILE_PATH is the path to a file which, when provided, will be where
this script writes its list of confirmation codes for each ballot.
"""

# core imports
import sys
import base, data, filenames

# based on meeting2, and meeting3 for the ballots
import meeting1, meeting2, meeting3
election = meeting1.election
ballots, cast_ballots = meeting3.ballots, meeting3.ballots_with_codes

# unused ballots codes
unused_ballots_codes_xml = base.file_in_dir(base.DATA_PATH, filenames.UNUSED_BALLOTS_CODES, 'Unused Ballots Codes')
unused_ballots = data.parse_ballot_table(unused_ballots_codes_xml)

# unused ballots mixnet
unused_ballots_mixnet_xml = base.file_in_dir(base.DATA_PATH, filenames.UNUSED_BALLOTS_MIXNET, 'Unused Ballots Mixnet')
unused_p_table, unused_partitions = data.parse_database(unused_ballots_mixnet_xml)

def verify(output_stream, codes_output_stream=None):

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

  # check codes
  for unused_ballot in unused_ballots.values():
    # does it verify against the original ballots
    assert ballots[unused_ballot.pid].verify_code_openings(unused_ballot, election.constant, code_callback_func = new_code)
  
  # we just verify that the D and P tables are opened properly
  # same as meeting2, only without a specific challenge set
  assert meeting2.verify_open_p_and_d_tables(election, meeting1.p_table, meeting1.partitions, unused_p_table, unused_partitions), "bad reveal of P and D tables"

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

  # go through the contested ballots
  output_stream.write("""Election ID: %s
Unused Ballots Audit Successful

%s ballots opened successfully

%s
""" % (election.spec.id, len(unused_ballots.keys()), base.fingerprint_report()))

if __name__ == '__main__':
  if len(sys.argv) > 2:
    codes_output = open(sys.argv[2], "w")
  else:
    codes_output = None
  verify(sys.stdout, codes_output)
  
  if codes_output:
    codes_output.close()