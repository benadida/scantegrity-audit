"""
The tallying of the R tables, no verification otherwise

Usage:
python tally.py <QUESTION_ID> <DATA_PATH> <DATA_PATH_2> <DATA_PATH_3> ... 

QUESTION_ID is the question_id from electionspec.xml
data paths should NOT have a trailing slash

More than one data path because we are tallying up multiple wards at the same time

The reason for specifying the question_num is that some questions are split among multiple wards, others not.

"""

# core imports
import sys
import base, data, filenames

import tallydata

# correcting the argv base.DATA_PATH
QUESTION_ID = sys.argv[1]
DATA_PATHS = sys.argv[2:]  

# for default election params
base.DATA_PATH = DATA_PATHS[0]

# use the meeting1 data structures
from electionparams import *

# import just the R tables
# there could be a few given the multiple data_paths
r_tables_xml = [base.file_in_dir(data_path, filenames.MEETING_THREE_OUT, 'Meeting Three Out') for data_path in DATA_PATHS]
r_tables_list = [data.parse_r_tables(r_tables) for r_tables in r_tables_xml]

print "ok now tallying\n\n"

# the list of partitions, each of which is a list of the max number of answers each question allows
partition_map = election.partition_map_choices

# we only tally per question now, so BALLOTS is just an array
BALLOTS = []
  
# go through each partition
for r_tables in r_tables_list:
  for p_id, r_table in r_tables.iteritems():
    for row_id, row in r_table.rows.iteritems():
      # split the result among questions for this partition, according to partition map
      split_result = r_table.get_permutations_by_row_id(row_id, partition_map[p_id])
    
      # go through the questions
      for q_num, question in enumerate(election.spec.questions_by_partition[p_id]):
        # skip over the questions we're not counting
        if question.id != QUESTION_ID:
          continue
        
        # index 0 because there is only one permutation field in this table,
        # but it's returned as a list, so we select the first and only one,
        # then select the specific question number
        raw_answer = split_result[0][q_num]
      
        # instantiate the right ballot type
        ballot = tallydata.BALLOTS_BY_TYPE[question.type_answer_choice](raw_answer)
      
        BALLOTS.append(ballot)

# now tally, only one tally
TALLY = BALLOTS[0].tally(election.spec.questions_by_id[QUESTION_ID], BALLOTS)

RESULT = "Question %s: %s\n" % (QUESTION_ID, TALLY)

def tally(output_stream):
  
  output_stream.write("""Election ID: %s
Tally

%s ballots cast

%s

""" % (election.spec.id, len(r_tables[0].rows), RESULT))

if __name__ == '__main__':
  tally(sys.stdout)