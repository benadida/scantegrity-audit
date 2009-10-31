"""
The tallying of the R tables, no verification otherwise

Usage:
python tally.py <DATA_PATH>

data path should NOT have a trailing slash
"""

# core imports
import sys
import base, data, filenames

import tallydata

# use the meeting1 data structures
from electionparams import *

# import just the R tables
r_tables_xml = base.file_in_dir(base.DATA_PATH, filenames.MEETING_THREE_OUT, 'Meeting Three Out')
r_tables = data.parse_r_tables(r_tables_xml)

print "ok now tallying\n\n"

# the list of partitions, each of which is a list of the max number of answers each question allows
partition_map = election.partition_map_choices

# indexed by "p_id/q_id", where each value is an array of ballots of the appropriate type
BALLOTS = {}

for question in election.spec.questions:
  BALLOTS[question.id] = []
  
# go through each partition
for p_id, r_table in r_tables.iteritems():
  for row_id, row in r_table.rows.iteritems():
    # split the result among questions for this partition, according to partition map
    split_result = r_table.get_permutations_by_row_id(row_id, partition_map[p_id])
    
    # go through the questions
    for q_num, question in enumerate(election.spec.questions_by_partition[p_id]):
      # index 0 because there is only one permutation field in this table,
      # but it's returned as a list, so we select the first and only one,
      # then select the specific question number
      raw_answer = split_result[0][q_num]
      
      # instantiate the right ballot type
      ballot = tallydata.BALLOTS_BY_TYPE[question.type_answer_choice](raw_answer)
      
      BALLOTS[question.id].append(ballot)

# now tally
TALLIES = {}

RESULTS = ""
for q_id in sorted(BALLOTS.keys()):
  TALLIES[q_id] = BALLOTS[q_id][0].tally(election.spec.questions_by_id[q_id], BALLOTS[q_id])
  RESULTS += "Question %s: %s\n" % (q_id, TALLIES[q_id])

def tally(output_stream):
  
  output_stream.write("""Election ID: %s
Tally

%s ballots cast

%s

""" % (election.spec.id, len(r_tables[0].rows), RESULTS))

if __name__ == '__main__':
  tally(sys.stdout)