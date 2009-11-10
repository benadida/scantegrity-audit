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
import meeting1, meeting2

# use provisional ballots as well
import meeting3provisional as meeting3

# fourth meeting
meeting_four_in_xml = base.file_in_dir(base.DATA_PATH, filenames.MEETING_FOUR_IN, 'Meeting Four In')
meeting_four_out_xml = base.file_in_dir(base.DATA_PATH, filenames.MEETING_FOUR_OUT, 'Meeting Four Out')
meeting_four_random_data = base.file_in_dir(base.DATA_PATH, filenames.MEETING_FOUR_RANDOM_DATA, "Random Data for Meeting Four Challenges", xml=False, correct_windows=True)

# from meeting1 and meeting 2
election, d_table_commitments, already_open_d_tables = meeting1.election, meeting1.partitions, meeting2.response_partitions
p_table_votes = meeting3.p_table_votes

# from meeting3, the D tables with intermediate decrypted votes
cast_ballot_partitions = data.parse_d_tables(meeting3.meeting_three_out_xml)

# challenge and response to those rows
d_table_challenges = data.parse_d_tables(meeting_four_in_xml)
d_table_responses = data.parse_d_tables(meeting_four_out_xml)

# r tables
r_tables_by_partition = data.parse_r_tables(meeting3.meeting_three_out_xml)

def verify(output_stream):
  # verify that challenges are appropriately generated
  challenges_match_randomness = True
  
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
  
  partition_map = election.partition_map
  partition_map_choices = election.partition_map_choices
  
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
          import pdb; pdb.set_trace()
          challenges_match_randomness = False

        # response row
        response_row = d_table_response.rows[row['id']]
        # partially decrypted choices, d3 out of d2,d3,d4, so index 1.
        try:
          d_choices = cast_ballot_partitions[p_id][instance_id].get_permutations_by_row_id(row['id'], partition_map_choices[p_id])[1]
        except:
          import pdb; pdb.set_trace()
          print "oy"

        # check the appropriate side  
        if row['side'] == 'LEFT':
          # check proper reveal
          assert d_table.check_cl(p_id, instance_id, response_row, election.constant)
          
          d_left_perm = [data.Permutation(p) for p in d_table_response.get_permutations_by_row_id(row['id'], partition_map[p_id])[0]]

          # get the corresponding P3 permutation (index 2, then partition)
          p_choices = p_table_votes.get_permutations_by_row_id(response_row['pid'], partition_map_choices)[2][p_id]

          for q_num, p_choice in enumerate(p_choices):
            assert d_left_perm[q_num].permute_list(p_choice) == d_choices[q_num]
        else:
          # check reveal
          assert d_table.check_cr(p_id, instance_id, response_row, election.constant)
          
          # check right-hand permutation
          d_right_perm = [data.Permutation(p) for p in d_table_response.get_permutations_by_row_id(row['id'], partition_map[p_id])[2]]

          # get the corresponding R-table permutation (partition, then index 0)
          r_choices = r_tables_by_partition[p_id].get_permutations_by_row_id(response_row['rid'], partition_map_choices[p_id])[0]
          
          for q_num, r_choice in enumerate(r_choices):
            assert d_right_perm[q_num].permute_list(d_choices[q_num]) == r_choice        
    
  output_stream.write("""Election ID: %s
Meeting 4 Successful

Challenges Match Randomness? %s

%s
""" % (election.spec.id, challenges_match_randomness, base.fingerprint_report()))

if __name__ == "__main__":
  verify(sys.stdout)