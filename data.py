"""
The data abstractions for Scantegrity Audit

ben@adida.net
2009-10-10
"""

from xml.etree import ElementTree

class PartitionInfo(object):
  """
  Maps a section/question to a partition
  
  A section ID or question ID can be any string, so we'll use dictionaries
  """
  def __init__(self):
    self.sections = {}
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

class Question(object):
  """
  A question's answers are represented as a position-ordered list of answer IDs.
  """
  def __init__(self, id, type_answer_choice, max_num_answers):
    self.id = id
    self.type_answer_choice = type_answer_choice
    self.max_num_answers = max_num_answers
    self.answers = []
    

class ElectionSpec(object):
  """
  Each section is a list of position-ordered questions
  
  parse from an electionspec.xml file
  """
  
  def __init__(self, partition_info):
    self.partition_info = partition_info
    self.sections = {}
  
  @staticmethod
  def _compare_positions(element_1, element_2):
    return cmp(int(element_1.attrib['possition']), int(element_2.attrib['possition']))
    
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
      self.sections[s.attrib['id']] = new_section = []
      
      questions = s.findall('questions/question')
      
      # sort them by "possition"
      questions.sort(ElectionSpec._compare_positions)
      
      # go through the questions, create question object
      for q in questions:
        q_object= Question(q.attrib['id'], q.attrib['typeOfAnswerChoice'], int(q.attrib['max_number_of_answers_selected']))
        new_section.append(q_object)
    
    
class Election(object):
  def __init__(self, election_spec):
    self.num_d_tables = 0
    self.num_ballots = 0
    self.constant = None
    self.spec = election_spec
    
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
  def __init__(self):
    self.rows = {}
  
  def parse(self, etree):
    # look for all rows
    for row_el in etree.findall('row'):
      self.rows[row_el.attrib['id']] = row_el.attrib
  
class PTable(Table):
  pass

class DTable(Table):
  pass
  
class RTable(object):
  pass


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
  
  # the P table
  p_table = PTable()
  p_table.parse(etree.find('database/print'))
  
  # the multiple D tables by partition
  partitions = {}
  partition_elements = etree.findall('database/partition')
  
  # go through each partition, each one is a dictionary of D-Table instances keyed by ID
  for partition_el in partition_elements:
    partitions[partition_el.attrib['id']] = new_partition = {}
    
    d_table_instances = partition_el.findall('decrypt/instance')
    for d_table_el in d_table_instances:
      new_partition[d_table_el.attrib['id']] = new_d_table = DTable()
      new_d_table.parse(d_table_el)
      
  return p_table, partitions

def parse_meeting_two_in(meeting_two_in_path):
  pass
  
def parse_meeting_two_out(meeting_two_out_path):
  pass