"""
The meeting one verification

Usage:
python meeting-one.py <DATA_PATH>

data path should NOT have a trailing slash
"""

import sys
import base, data, filenames

# base election params
from electionparams import *

# get the election data
meeting_one_out_xml = base.file_in_dir(base.DATA_PATH, filenames.MEETING_ONE_OUT, "Meeting One Out")

# get the p table and d tables
p_table, partitions = data.parse_database(meeting_one_out_xml)

# are we actually running meeting 1?
def verify(output_stream):
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
    
  output_stream.write("""Election ID: %s
Meeting 1 Successful

%s Ballots
Partitions: %s
%s D-Tables

%s
""" % (election.spec.id, election.num_ballots, partitions.keys(), num_d_tables, base.fingerprint_report()))

if __name__ == '__main__':
  verify(sys.stdout)