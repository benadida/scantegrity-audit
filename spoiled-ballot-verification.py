"""
The spoiled ballot verification

Usage:
python spoiled-ballot-verification.py <DATA_PATH>

data path should NOT have a trailing slash
"""

# core imports
import sys
import base, data, filenames

# based on meeting2, and meeting3 for the ballots
import meeting1, meeting2, meeting3
election = meeting1.election
ballots, cast_ballots = meeting3.ballots, meeting3.ballots_with_codes

# spoiled ballots codes
spoiled_ballots_codes_xml = base.file_in_dir(base.DATA_PATH, filenames.SPOILED_BALLOTS_CODES, 'Spoiled Ballots Codes')
spoiled_ballots = data.parse_ballot_table(spoiled_ballots_codes_xml)

# spoiled ballots mixnet
spoiled_ballots_mixnet_xml = base.file_in_dir(base.DATA_PATH, filenames.SPOILED_BALLOTS_MIXNET, 'Spoiled Ballots Mixnet')
spoiled_p_table, spoiled_partitions = data.parse_database(spoiled_ballots_mixnet_xml)

def verify(output_stream):
  # check codes
  for spoiled_ballot in spoiled_ballots.values():
    # does it verify against the original ballots
    assert ballots[spoiled_ballot.pid].verify_code_openings(spoiled_ballot, election.constant)
  
  # we just verify that the D and P tables are opened properly
  # same as meeting2, only without a specific challenge set
  assert meeting2.verify_open_p_and_d_tables(election, meeting1.p_table, meeting1.partitions, spoiled_p_table, spoiled_partitions), "bad reveal of P and D tables"

  # go through the contested ballots
  output_stream.write("""Election ID: %s
Spoiled Ballots Audit Successful

%s ballots spoiled and opened successfully

%s
""" % (election.spec.id, len(spoiled_ballots.keys()), base.fingerprint_report()))

if __name__ == '__main__':
  verify(sys.stdout)