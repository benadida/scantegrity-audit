"""
The meeting four verification

Usage:
python meeting4.py <DATA_PATH>

data path should NOT have a trailing slash
"""

# core imports
import sys
import base, data, filenames

# use the meeting1,2,3 data structures too
import meeting1, meeting2, meeting3

# fourth meeting
meeting_four_in_xml = base.file_in_dir(base.DATA_PATH, filenames.MEETING_FOUR_IN, 'Meeting Four In')
meeting_four_out_xml = base.file_in_dir(base.DATA_PATH, filenames.MEETING_FOUR_OUT, 'Meeting Four Out')
meeting_four_random_data = base.file_in_dir(base.DATA_PATH, filenames.MEETING_FOUR_RANDOM_DATA, "Random Data for Meeting Four Challenges", xml=False)

# from meeting1 and meeting 2
election, d_table_commitments, already_open_d_tables = meeting1.election, meeting1.partitions, meeting2.response_partitions

# from meeting3, the D tables with intermediate decrypted votes
cast_ballot_partitions = data.parse_d_tables(meeting3.meeting_three_out_xml)

# challenge and response to those rows
d_table_challenges = data.parse_d_tables(meeting_four_in_xml)
d_table_responses = data.parse_d_tables(meeting_four_out_xml)

# r tables
r_tables_by_partition = data.parse_r_tables(meeting3.meeting_three_out_xml)

def verify(output_stream):
  # verify that challenges are appropriately generated
  challenges_match_randomness = False
  
  # we assume that one D table always opens on the same side
  # we do a bit of an odd thing here to keep the partitions and d tables in order
  # because that's how counter is decided
  counter = 0
  
  # a dictionary of partition_ids, with values a dictionary of d_table ID
  expected_challenge_sides = {}
  
  seed = meeting_four_random_data + election.constant
  
  for p_id in sorted(cast_ballot_partitions.keys()):
    partition = cast_ballot_partitions[p_id]
    expected_challenge_sides[p_id] = {}
    
    # get the D tables ordered by their integer ID
    for d_table in data.sort_by_id(partition.values()):
      instance_id = d_table.id
      
      # which side is this d table opened on?
      expected_challenge_sides[p_id][instance_id] = ("LEFT","RIGHT")[base.prng(seed,counter,2)]
      counter += 1
  
  # go through the challenges and verify the corresponding commitments
  for p_id, partition in d_table_challenges.iteritems():
    for instance_id, d_table_challenge in partition.iteritems():
      
      d_table = d_table_commitments[p_id][instance_id]
      d_table_response = d_table_responses[p_id][instance_id]
      
      # check that the open rows now are disjoint from the open rows before
      assert set(d_table_challenge.rows.keys()).isdisjoint(set(already_open_d_tables[p_id][instance_id].rows.keys())), 'some challenges repeat the challenges from meeting2'
      
      # check opening of the new challenges
      for row in d_table_challenge.rows.values():
        # does it match the randomness?
        if row['side'] != expected_challenge_sides[p_id][instance_id]:
          challenges_match_randomness = False
        
        # check the appropriate side  
        if row['side'] == 'LEFT':
          assert d_table.check_cl(p_id, instance_id, d_table_response.rows[row['id']], election.constant)
          # FIXME: check that permutation probably transforms P-table row into this row
        else:
          assert d_table.check_cr(p_id, instance_id, d_table_response.rows[row['id']], election.constant)          
          # FIXME: check that permutation probably transforms this row into R-table row
        
    
  output_stream.write("""Election ID: %s
Meeting 4 Successful

Challenges Match Randomness? %s

%s
""" % (election.spec.id, challenges_match_randomness, base.fingerprint_report()))

if __name__ == "__main__":
  verify(sys.stdout)