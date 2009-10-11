"""
The data abstractions for Scantegrity Audit

ben@adida.net
2009-10-10
"""

from xml.etree import ElementTree
import commitment

def _compare_positions(element_1, element_2):
  """
  a function to help sort elements that have a position attribute
  misspelled in the spec as 'possition'
  """
  return cmp(int(element_1.attrib['possition']), int(element_2.attrib['possition']))

##
## Permutations
##

def split_permutations(concatenated_permutations, partition_map):
  """
  Given concatenated permutations and a partition_map, i.e. [[2],[3,4]],
  split things up into the appropriate tree structure of permutations
  
  done recursively, with base condition the partition_map being just an integer
  of the number of answers
  """
  # this is uglier than it needs to be because of weird Python local variable
  # conflicts with closures
  
  def walk_map(p_map, current_index):
    if type(p_map) == list:
      perms = []
      for el in p_map:
        new_perm, current_index = walk_map(el, current_index)
        perms.append(new_perm)
      return perms, current_index
    else:
      new_index = current_index + p_map
      return concatenated_permutations[current_index:new_index], new_index
  
  return walk_map(partition_map, 0)[0]
  
def compose_permutations(perm_1, perm_2):
  """
  apply permutation 1 first, then permutation 2
  both represented as 0-indexed arrays
  """
  return [perm2[i] for i in perm_1]
  
##
## Data Structures
##
  
class PartitionInfo(object):
  """
  Maps a section/question to a partition
  
  A section ID or question ID can be any string, so we'll use dictionaries
  """
  def __init__(self):
    self.sections = {}
    self.partitions = []
    self.id = None
  
  def parse(self, etree):
    """
    parse from an elementtree.
    """
    self.id = etree.find('electionInfo').attrib['id']
    
    # go through each section
    sections = etree.findall('electionInfo/sections/section')
    for s in sections:
      # add the section by its identifier
      self.sections[s.attrib['id']] = new_section = {}
      
      # find all questions
      questions = s.findall('questions/question')
      for q in questions:
        # add mapping of question to partition n., which is an integer
        new_section[q.attrib['id']] = int(q.attrib['partitionNo'])
    
    # figure out the partitions
    num_partitions = max([max(section.values()) for section in self.sections.values()]) + 1
    
    # set up the partitions as lists of questions within each partition
    self.partitions = [[] for i in range(num_partitions)]
    
    # index the questions by partition
    for s_id, section in self.sections.iteritems():
      for q_id, q_partition in section.iteritems():
        self.partitions[q_partition].append({'section_id': s_id, 'question_id': q_id})
        
    # we're assuming here that the ordering within the partitions is correct
    # because the documentation says nothing more
        
class Question(object):
  """
  A question's answers are represented as a position-ordered list of answer IDs.
  """
  def __init__(self):
    self.id = None
    self.type_answer_choice = None
    self.max_num_answers = None
    self.answers = None
    
  def parse(self, etree):
    """
    parse the answers
    """
    self.id = etree.attrib['id']
    self.type_answer_choice = etree.attrib['typeOfAnswerChoice']
    self.max_num_answers = int(etree.attrib['max_number_of_answers_selected'])
    
    self.answers = etree.findall('answers/answer')
    self.answers.sort(_compare_positions)

class ElectionSpec(object):
  """
  Each section is a list of position-ordered questions
  
  parse from an electionspec.xml file
  """
  
  def __init__(self, partition_info):
    self.partition_info = partition_info
    self.sections = {}
    
    # a linear list of all the questions, when the sections don't matter
    self.questions = []
  
  def parse(self, etree):
    self.id = etree.find('electionInfo').attrib['id']

    # check match of election IDs
    if self.partition_info and self.partition_info.id != self.id:
      import pdb; pdb.set_trace()
      raise Exception("election IDs don't match")
      
    # go through each section
    sections = etree.findall('electionInfo/sections/section')
    for s in sections:
      # add the section by its identifier
      self.sections[s.attrib['id']] = new_section = {}
      
      questions = s.findall('questions/question')
      
      # sort them by "possition"
      questions.sort(_compare_positions)
      
      # go through the questions, create question object
      for q in questions:
        q_object= Question()
        q_object.parse(q)
        new_section[q.attrib['id']] = q_object
        self.questions.append(q_object)
    
    
class Election(object):
  def __init__(self, election_spec):
    self.num_d_tables = 0
    self.num_ballots = 0
    self.constant = None
    self.spec = election_spec
    
  @property
  def partition_map(self):
    # list of lists of dictionaries, each dictionary contains the question and section IDs
    partitions = self.spec.partition_info.partitions
    
    import pdb; pdb.set_trace()
    
    # look up the number of answers for each question within each section
    return [[len(self.spec.sections[q_info['section_id']][q_info['question_id']].answers) for q_info in partition] for partition in partitions]

  def parse(self, etree):
    """
    parse from the MeetingOneIn file
    """
    self.num_d_tables = int(etree.findtext('noDs'))
    self.num_ballots = int(etree.findtext('noBallots'))
    self.constant = etree.findtext('constant')

class Table(object):
  """
  A base table class that has features that P, D, and R tables all need
  """
  
  # fields that are to be interpreted as permutations
  PERMUTATION_FIELDS = []
  
  def __init__(self):
    self.rows = {}
    
  @classmethod
  def process_row(cls, row):
    """
    for the fields that are interpreted as permutations,
    do proper splitting on spaces to create python lists
    """
    for f in cls.PERMUTATION_FIELDS:
      if row.has_key(f):
        row[f] = [int(el) for el in row[f].split(' ')]
    
    return row
  
  def parse(self, etree):
    # look for all rows
    for row_el in etree.findall('row'):
      self.rows[row_el.attrib['id']] = self.process_row(row_el.attrib)
  
class PTable(Table):
  PERMUTATION_FIELDS = ['p1', 'p2']
  
  def __init__(self):
    super(PTable, self).__init__()
    self.__permutations_by_row_id = {}
    
  @classmethod
  def __check_commitment(cls, commitment_str, row_id, permutation, salt, constant):
    """
    check the reveal of a commitment to a permutation,
    """
    # prepare the string that we are committing to
    message = row_id
    message += ''.join([chr(el) for el in permutation])

    # reperform commitment and check equality
    return commitment_str == commitment.commit(message, salt, constant)
    
  def check_c1(self, reveal_row, constant):
    return self.__check_commitment(self.rows[reveal_row['id']]['c1'], reveal_row['id'], reveal_row['p1'], reveal_row['s1'], constant)
  
  def check_c2(self, reveal_row, constant):
    return self.__check_commitment(self.rows[reveal_row['id']]['c2'], reveal_row['id'], reveal_row['p2'], reveal_row['s2'], constant)
    
  def check_full_row(self, reveal_row, constant):
    return self.check_c1(reveal_row, constant) and self.check_c2(reveal_row, constant)
    
  def permutations_by_row_id(self, row_id, pmap):
    # already computed?
    if not self.__permutations_by_row_id.has_key(row_id):
      self.__permutations_by_row_id[row_id] = split_permutations(self.rows[row_id]['p1'], pmap), split_permutations(self.rows[row_id]['p2'], pmap)
      
    return self.__permutations_by_row_id[row_id]

class DTable(Table):
  PERMUTATION_FIELDS = ['d2', 'd4']

  @classmethod
  def __check_commitment(cls, commitment_str, partition_id, instance_id, row_id, external_id, permutation, salt, constant):
    """
    check the reveal of a commitment to a permutation,
    the "external_id" is the reference to the other table, either pid or rid
    """
    # prepare the string that we are committing to
    message = chr(partition_id) + chr(instance_id) + row_id + external_id
    message += ''.join([chr(el) for el in permutation])

    # reperform commitment and check equality
    return commitment_str == commitment.commit(message, salt, constant)
  
  def check_cl(self, partition_id, instance_id, reveal_row, constant):
    relevant_row = self.rows[reveal_row['id']]
    return self.__check_commitment(relevant_row['cl'], partition_id, instance_id, relevant_row['id'], reveal_row['pid'], reveal_row['d2'], reveal_row['sl'], constant)

  def check_cr(self, partition_id, instance_id, reveal_row, constant):
    relevant_row = self.rows[reveal_row['id']]
    return self.__check_commitment(relevant_row['cr'], partition_id, instance_id, relevant_row['id'], reveal_row['rid'], reveal_row['d4'], reveal_row['sr'], constant)
    
  def check_full_row(self, *args):
    return self.check_cl(*args) and self.check_cr(*args)
  
class RTable(object):
  pass

##
## some reusable utilities
##

def parse_database(etree):
  """
  parses a P table and a bunch of D tables, which happens a few times
  
  The partition_id and instance_id are integers
  """
  
  # the P table
  p_table = PTable()
  p_table.parse(etree.find('database/print'))
  
  # the multiple D tables by partition
  partitions = {}
  partition_elements = etree.findall('database/partition')
  
  # go through each partition, each one is a dictionary of D-Table instances keyed by ID
  for partition_el in partition_elements:
    partitions[int(partition_el.attrib['id'])] = new_partition = {}
    
    d_table_instances = partition_el.findall('decrypt/instance')
    for d_table_el in d_table_instances:
      new_partition[int(d_table_el.attrib['id'])] = new_d_table = DTable()
      new_d_table.parse(d_table_el)
      
  return p_table, partitions


def parse_meeting_one_in(partitions_path, election_spec_path, meeting_one_in_path):
  partition_info = PartitionInfo()
  partition_info.parse(ElementTree.parse(partitions_path))
  
  election_spec = ElectionSpec(partition_info)
  election_spec.parse(ElementTree.parse(election_spec_path))
  
  election = Election(election_spec)
  election.parse(ElementTree.parse(meeting_one_in_path))
  
  return election
  

def parse_meeting_one_out(meeting_one_out_path):
  etree = ElementTree.parse(meeting_one_out_path)
  
  return parse_database(etree)
  
def parse_meeting_two_in(meeting_two_in_path):
  etree = ElementTree.parse(meeting_two_in_path)
  
  # the P table of challenges
  p_table = PTable()
  p_table.parse(etree.find('challenges/print'))
  
  return p_table
  
def parse_meeting_two_out(meeting_two_out_path):
  etree = ElementTree.parse(meeting_two_out_path)
  
  return parse_database(etree)
