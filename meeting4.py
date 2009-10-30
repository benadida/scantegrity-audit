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

# from meeting1 and meeting 2
election, d_table_commitments, already_open_d_tables = meeting1.election, meeting1.partitions, meeting2.response_partitions

# challenge and response to those rows
d_table_challenges = data.parse_d_tables(meeting_four_in_xml)
d_table_responses = data.parse_d_tables(meeting_four_out_xml)

def verify(output_stream):
  # go through the challenges and verify the corresponding commitments
  for p_id, partition in d_table_challenges.iteritems():
    for instance_id, d_table_challenge in partition.iteritems():
      
      d_table = d_table_commitments[p_id][instance_id]
      d_table_response = d_table_responses[p_id][instance_id]
      
      # check that the open rows now are disjoint from the open rows before
      assert set(d_table_challenge.rows.keys()).isdisjoint(set(already_open_d_tables[p_id][instance_id].rows.keys())), 'some challenges repeat the challenges from meeting2'
      
      # check opening of the new challenges
      for row in d_table_challenge.rows.values():
        if row['side'] == 'LEFT':
          assert d_table.check_cl(p_id, instance_id, d_table_response.rows[row['id']], election.constant)
        else:
          assert d_table.check_cr(p_id, instance_id, d_table_response.rows[row['id']], election.constant)          
        
    
  output_stream.write("""Election ID: %s
Meeting 4 Successful

%s
""" % (election.spec.id, base.fingerprint_report()))

if __name__ == "__main__":
  verify(sys.stdout)