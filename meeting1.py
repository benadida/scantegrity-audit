"""
The meeting one verification

Usage:
python meeting-one.py <DATA_PATH>

data path should NOT have a trailing slash
"""

from meetingbase import *

# get the election data
partition_xml = file_in_dir(DATA_PATH, PARTITIONS, 'Partition File')
election_xml = file_in_dir(DATA_PATH, ELECTION_SPEC, 'Election Spec')
meeting_one_in_xml = file_in_dir(DATA_PATH, MEETING_ONE_IN, 'Meeting One In')
meeting_one_out_xml = file_in_dir(DATA_PATH, MEETING_ONE_OUT, "Meeting One Out")

# parse
partition_info = PartitionInfo()
partition_info.parse(partition_xml)

election_spec = ElectionSpec(partition_info)
election_spec.parse(election_xml)

election = Election(election_spec)
election.parse(meeting_one_in_xml)

# get the p table and d tables
p_table, partitions = parse_database(meeting_one_out_xml)

# are we actually running meeting 1?
if __name__ == '__main__':
  # check that there are as many ballots in the P table as claimed
  assert len(p_table.rows) == election.num_ballots, "P Table has the wrong number of ballots, should be %s " % election.num_ballots

  num_d_tables = None

  # loop through partitions
  for p_id, partition in partitions.iteritems():
    this_num_d_tables = len(partition.values())
  
    # check that it's the same number of D tables
    if num_d_tables:
      assert this_num_d_tables == num_d_tables
    else:
      num_d_tables = this_num_d_tables
    
    # loop through d tables for that partition
    for d_table_id, d_table in partition.iteritems():
      # check that it has the right number of ballots
      assert len(d_table.rows) == election.num_ballots, "D Table %s in partition %s has the wrong number of ballots, should be %s" % (d_table_id, p_id, election.num_ballots)
    
  print """Election ID: %s
Meeting 1 Successful

%s Ballots
Partitions: %s
%s D-Tables

%s
""" % (election.spec.id, election.num_ballots, partitions.keys(), num_d_tables, fingerprint_report())