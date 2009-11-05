"""
The data abstractions for plaintext ballot tallying
part of Scantegrity Audit code

ben@adida.net
2009-10-31
"""

BALLOTS_BY_TYPE = {}

class RankBallot(object):
  def __init__(self, raw_data):
    # split the raw data into array of choices
    self.choices = raw_data
    self.exhausted = False
    
    self.reset()

  def go_next_choice(self, choice_to_cancel):
    if self.exhausted:
      return
      
    if self.current_choice == choice_to_cancel: 
      self.__current_index += 1
    
      if self.current_choice == None:
        self.exhausted = True
  
  @property
  def current_choice(self):
    if self.exhausted:
      return None
    
    if len(self.choices) <= self.__current_index:
      return None
      
    if self.choices[self.__current_index] == -1:
      return None
      
    return self.choices[self.__current_index]
    
  def reset(self):
    self.__current_index = 0
    self.exhausted = (self.current_choice == None)
    
  @classmethod
  def tally(cls, question, ballots):
    """
    tally a bunch of ranked ballots.
    Could be easily improved for efficiency, but went for obviously correct code first.
    Plus, this is pretty quick anyways
    """
    # if we round to the half, we increment by 1
    absolute_majority = len(ballots) / 2 + len(ballots)%2 + 1
    
    eliminated = []
    # eliminate and redistribute until done
    while True:
      candidate_tallies = [0] * len(question.answers)
      for i in eliminated:
        candidate_tallies[i] = None

      try:
        # count
        for b in ballots:
          if not b.exhausted:
            candidate_tallies[b.current_choice] += 1
      except Exception, e:
        import pdb; pdb.set_trace()
        bad_ballot = b
        print "oy"
      
      # print candidate_tallies

      if max(candidate_tallies) >= absolute_majority:
        break
        
      # eliminate
      lowest_count = min([tally for tally in candidate_tallies if tally is not None])
      lowest_count_index = candidate_tallies.index(lowest_count)
      eliminated.append(lowest_count_index)
      #print "eliminating candidate %s with count %s" % (lowest_count_index, lowest_count)
      for b in ballots:
        b.go_next_choice(lowest_count_index)
    
    return candidate_tallies

class SimpleBallot(object):
  def __init__(self, raw_data):
    # split the raw data into array of choices
    self.choices = raw_data

  @classmethod
  def tally(cls, question, ballots):
    """
    tally a bunch of ballots where choices are just single or multi candidate.
    """
    candidate_tallies = [0] * len(question.answers)
    
    for b in ballots:
      for option in b.choices:
        candidate_tallies[option] += 1
    
    return candidate_tallies
  
      
BALLOTS_BY_TYPE['rank'] = RankBallot
BALLOTS_BY_TYPE['one_answer'] = SimpleBallot
BALLOTS_BY_TYPE['multiple_answers'] = SimpleBallot