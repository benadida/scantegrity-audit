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

def walk_permutation_map(p_map, func, running_data):
  """
  walk a permutation map and apply a func at the base, with extra args
  passed and returned along the way
  """
  # this is uglier than it needs to be because of weird Python local variable
  # conflicts with closures
  
  if type(p_map) == list:
    perms = []
    for el in p_map:
      new_perm, running_data = walk_permutation_map(el, func, running_data)
      perms.append(new_perm)
    return perms, running_data
  else:
    return func(p_map, running_data)
  
def split_permutations(concatenated_permutations, partition_map):
  """
  Given concatenated permutations [0 1 2 0 1 0 2 3 1] and a partition_map, i.e. [[2],[3,4]],
  split things up into the appropriate tree structure of permutations: [[[0 1]], [[2 0 1], [0 2 3 1]]]

  This is also used to split the p3 column of the P table, where instead of permutations, we are dealing with
  actual voter selections of candidates. In that case, the partition map should list the max_num_answers,
  not the total_num_answers.

  assumes that a partition map is either a list of num_anwers (one partition)
  or a list of lists of num_answers (many partitions)
  """
  
  # a function to extract the permutation when we get to the leaf
  def subperm(p_map, current_index):
    new_index = current_index + p_map
    return concatenated_permutations[current_index:new_index], new_index
  
  return walk_permutation_map(partition_map, subperm, 0)[0]
  
def compose_permutations(list_of_perms):
  """
  apply permutation 1 first, then permutation 2, then...
  both represented as 0-indexed arrays
  """
  perm = list_of_perms[0]
  for p in list_of_perms[1:]:
    # [2 0 1] o [1 2 0]
    # apply the next perm
    perm = [p[i] for i in perm]
  return perm

def inverse_permutation(perm):
  """
  inverse a permutation
  """
  # copy it
  new_perm = range(len(perm))
  
  for i in range(len(perm)):
    new_perm[perm[i]] = i
    
  return new_perm

def compose_lists_of_permutations(list_of_perms_1, list_of_perms_2):
  """
  two lists of permutations, where corresponding indexes into each need to be composed with one another
  """
  return [compose_permutations([list_of_perms_1[i], list_of_perms_2[i]]) for i in range(len(list_of_perms_1))]
    

  
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
    
  def partition_num(self, section_id, question_id):
    return self.sections[section_id][question_id]
  
  @property
  def num_partitions(self):
    return len(self.partitions)
  
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
    self.section_id = None
    self.partition_num = None
    
  def parse(self, etree, section_id, partition_info):
    """
    parse the answers
    """
    self.id = etree.attrib['id']
    self.type_answer_choice = etree.attrib['typeOfAnswerChoice']
    self.max_num_answers = int(etree.attrib['max_number_of_answers_selected'])
    
    self.answers = etree.findall('answers/answer')
    self.answers.sort(_compare_positions)
    
    self.section_id = section_id
    self.partition_num = partition_info.partition_num(self.section_id, self.id)

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
    
    # a list of questions by partition
    self.questions_by_partition = []
    
  def lookup_question(self, section_id, question_id):
    return self.sections[section_id][question_id]
  
  def lookup_question_from_partition_info(self, q_info):
    return self.lookup_question(self, q_info['section_id'], q_info['question_id'])
  
  def parse(self, etree):
    self.id = etree.find('electionInfo').attrib['id']

    # check match of election IDs
    if self.partition_info and self.partition_info.id != self.id:
      import pdb; pdb.set_trace()
      raise Exception("election IDs don't match")
    
    # initialize the questions_by_partition
    self.questions_by_partition = [[] for i in range(self.partition_info.num_partitions)]
    
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
        q_object.parse(q, s.attrib['id'], self.partition_info)
        
        new_section[q.attrib['id']] = q_object
        self.questions.append(q_object)
        self.questions_by_partition[q_object.partition_num].append(q_object)
    
    
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
    
    # look up the number of answers for each question within each section
    return [[len(self.spec.sections[q_info['section_id']][q_info['question_id']].answers) for q_info in partition] for partition in partitions]

  @property
  def partition_map_choices(self):
    """
    same as partition map, only with the max num of selected answers for each question,
    rather than the total num of answers to choose from. Useful for parsing the voter selection.
    """
    # list of lists of dictionaries, each dictionary contains the question and section IDs
    partitions = self.spec.partition_info.partitions

    # look up the number of answers for each question within each section
    return [[q_info.max_num_answers for q_info in partition] for partition in partitions]

  @property
  def num_partitions(self):
    """
    A list of partition IDs
    """
    return len(self.spec.partition_info.partitions)
  
  def questions_in_partition(self, partition_num):
    """
    list of question objects in a given partition
    """
    return self.spec.questions_by_partition[partition_num]
    
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
    self.__permutations_by_row_id = {}
    
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

  def get_permutations_by_row_id(self, row_id, pmap):
    # already computed?
    if not self.__permutations_by_row_id.has_key(row_id):
      self.__permutations_by_row_id[row_id] = [split_permutations(self.rows[row_id][perm_field], pmap) for perm_field in self.PERMUTATION_FIELDS]

    return self.__permutations_by_row_id[row_id]

  def get_composed_permutations_by_row_id(self, row_id, pmap):
    """
    assume for now that pmap is one-level deep only
    """
    perms = self.get_permutations_by_row_id(row_id, pmap)
    
    # now compose them
    
    
  def parse(self, etree):
    # look for all rows
    for row_el in etree.findall('row'):
      self.rows[row_el.attrib['id']] = self.process_row(row_el.attrib)
  
class PTable(Table):
  PERMUTATION_FIELDS = ['p1', 'p2']
      
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
  
class Ballot(object):
  """
  represents the printed ballot information, with commitments and confirmation codes
  """
  def __init__(self, etree=None):    
    # dictionary of questions, each is a dictionary of symbols
    self.questions = {}
    
    if etree:
      self.parse(etree)
      
  def verify_code_openings(self, open_ballot, constant, marked_codes_db = None):
    """
    this ballot is the commitment, the other ballot is the opening.
    
    The marked_codes_db is an object that, if present, should support one method call:
    marked_codes_db.add_code(web_serial_num, pid, question_id, symbol_id, confirmation_code)
    
    This is called only when a code is successfully verified, and enables bookkeeping of
    codes to show the voters in a verification interface.
    """
    
    # pid match
    if self.pid != open_ballot.pid:
      return False
    
    # check opening of web serial number
    if self.webSerialCommitment != commitment.commit(self.pid + " " + open_ballot.webSerial, open_ballot.webSerialSalt, constant):
      return False
    
    # check opening of all marked codes
    for q_id, q in open_ballot.questions.iteritems():
      # the symbols for this ballot
      committed_symbols = self.questions[q_id]
      
      # go through the open symbols
      for s_id, s in q.iteritems():
        if committed_symbols[s_id]['c'] != commitment.commit(" ".join([self.pid, q_id, s_id, s['code']]), s['salt'], constant):
          return False
          
        # record the code for this ballot
        if marked_codes_db:
          marked_codes_db.add_code(open_ballot.webSerial, self.pid, q_id, s_id, s['code'])          
  
    # only if all tests pass, then succeed
    return True
    
  def parse(self, etree):
    # add all of the attributes
    self.__dict__.update(etree.attrib)
    
    for q_el in etree.findall('question'):
      self.questions[q_el.attrib['id']] = new_q = {}
      
      for symbol_el in q_el.findall('symbol'):
        new_q[symbol_el.attrib['id']] = symbol_el.attrib

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

def parse_ballot_table(ballot_table_path):
  etree = ElementTree.parse(ballot_table_path)
  
  # the ballots
  ballot_elements = etree.findall('database/printCommitments/ballot')
  
  return dict([(b.pid, b) for b in [Ballot(e) for e in ballot_elements]])
  
def parse_meeting_two_out_commitments(meeting_two_out_commitments_path):
  return parse_ballot_table(meeting_two_out_commitments_path)
  
def parse_meeting_three_in(meeting_three_in_path):
  etree = ElementTree.parse(meeting_three_in_path)
  
  # it's just a P table
  p_table = PTable()
  p_table.parse(etree.find('print'))
  
  return p_table

def parse_meeting_three_out_codes(meeting_three_out_codes_path):
  return parse_ballot_table(meeting_three_out_codes_path)
