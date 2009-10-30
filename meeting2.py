"""
The meeting two verification

Usage:
python meeting2.py <DATA_PATH>

data path should NOT have a trailing slash
"""

from meeting1 import *

# second meeting
meeting_two_in_xml = file_in_dir(DATA_PATH, MEETING_TWO_IN, 'Meeting Two In')
meeting_two_out_xml = file_in_dir(DATA_PATH, MEETING_TWO_OUT, "Meeting Two Out")
meeting_two_out_commitments_xml = file_in_dir(DATA_PATH, MEETING_TWO_OUT_COMMITMENTS, "Meeting Two Out Commitments")
meeting_two_random_data = file_in_dir(DATA_PATH, MEETING_TWO_RANDOM_DATA, "Random Data for Meeting Two Challenges", xml=False)

# get the challenges
challenge_p_table = PTable()
challenge_p_table.parse(meeting_two_in_xml.find('challenges/print'))

# get the response
response_p_table, response_partitions = parse_database(meeting_two_out_xml)

challenge_row_ids = challenge_p_table.rows.keys()

# actual meeting two verifications
if __name__ == '__main__':  
  p_table_permutations = {}
  
  # check the generation of the challenge rows
  challenge_row_ids_ints = [int(c) for c in challenge_row_ids]
  
  # we assume that the length of the challenge list is the right one
  challenges_match_randomness = False
  if challenge_row_ids_ints == generate_random_int_list(meeting_two_random_data, election.num_ballots, len(challenge_row_ids)):
    challenges_match_randomness = True
  
  # check the P table commitments
  for row_id in challenge_row_ids:
    assert p_table.check_full_row(response_p_table.rows[row_id], election.constant), "commitment doesn't match in P table"
  
  # Now we go through the partitions, the d tables within each partition,
  # and we look at the rows that are revealed. As we do this, we'll also
  # spot check that the permutations in a given d_table row match the p_table permutations
  # for that question.
  
  # first we get the partition-and-question map for this election, which
  # is effectively a tree representation of how the questions are grouped
  # in partitions, with each leaf being the number of answers for that given question.
  partition_map = election.partition_map
  
  # loop through partitions
  for p_id, partition in partitions.iteritems():
    # loop through d tables for that partition
    for d_table_id, d_table in partition.iteritems():
      # get the corresponding response D table
      response_d_table = response_partitions[p_id][d_table_id]
      
      # for efficiency of lookup, so we don't have to look up D-table rows by p-table row ID
      # (which we haven't indexed), we check that
      # (1) the responses are correct according to the commitments
      # (2) the list of p_id rows in each response set matches the challenge row IDs
      
      # (1) reveals match
      for row_id, response_row in response_d_table.rows.iteritems():
        assert d_table.check_full_row(p_id, d_table_id, response_row, election.constant), "bad d table commitment"
      
      # (2) list of p_ids matches
      assert sorted(challenge_row_ids) == sorted([r['pid'] for r in response_d_table.rows.values()])
      
      # (3) permutations
      for row_id, response_row in response_d_table.rows.iteritems():
        d_perm_left, d_perm_right = response_d_table.get_permutations_by_row_id(row_id, partition_map[p_id])
        
        p_row_id = response_d_table.rows[row_id]['pid']
        
        # get the corresponding P table permutation subset
        p_perms_full = response_p_table.get_permutations_by_row_id(p_row_id, partition_map)
        p_perm_1, p_perm_2 = [perms[p_id] for perms in p_perms_full]
        
        ## compare the compositions
        
        # on the d table, just d2 then d4 to go from coded to decoded
        d_composed = compose_lists_of_permutations(d_perm_left, d_perm_right)
        
        # the composition of the print tables is p_2 o p_1_inv to go from coded to decoded
        p_composed = compose_lists_of_permutations(p_perm_2, [inverse_permutation(p) for p in p_perm_1])
        
        assert d_composed == p_composed, "PERMUTATION PROBLEM %s/%s/%s: %s --- %s" % (p_id, d_table_id, row_id, d_composed, p_composed)
      
  
  print """Election ID: %s
Meeting 2 Successful

%s ballots challenged and answered successfully.

Challenges Match Randomness? %s

%s
""" % (election.spec.id, len(challenge_row_ids), str(challenges_match_randomness).upper(), fingerprint_report())