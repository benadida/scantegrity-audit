"""
The contested ballot verification

Usage:
python contested-ballot-verification.py <DATA_PATH>

data path should NOT have a trailing slash
"""

# core imports
import sys
import base, data, filenames

# based on meeting2, and meeting3 for the ballots which aren't needed for parsing until then, nothing in meeting4 needed
import meeting1, meeting2, meeting3
election = meeting1.election
ballots, cast_ballots = meeting3.ballots, meeting3.ballots_with_codes

# contested ballots reveal
contested_ballots_reply_xml = base.file_in_dir(base.DATA_PATH, filenames.CONTESTED_BALLOTS_REPLY, 'Reply to Contested Ballots')
contested_ballots = data.parse_ballot_table(contested_ballots_reply_xml)

def verify(output_stream):
  # for each contested ballot:
  for contested_ballot in contested_ballots.values():
    # is it a cast ballot?
    assert cast_ballots.has_key(contested_ballot.pid)
    
    # does it verify against the original ballots
    assert ballots[contested_ballot.pid].verify_code_openings(contested_ballot, election.constant)
    
  # go through the contested ballots
  output_stream.write("""Election ID: %s
Contested Ballots Audit Successful

%s ballots contested and opened successfully

%s
""" % (election.spec.id, len(contested_ballots.keys()), base.fingerprint_report()))

if __name__ == '__main__':
  verify(sys.stdout)