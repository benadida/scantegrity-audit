"""
filenames for individual audit files

Ben Adida
ben@adida.net
2009-10-10
"""

import hashlib

# first meeting
MEETING_ONE_IN = "MeetingOneIn.xml"
MEETING_ONE_OUT = "MeetingOneOut.xml"
ELECTION_SPEC = "ElectionSpec.xml"
PARTITIONS = "partitions.xml"

# second meeting
MEETING_TWO_IN = "MeetingTwoIn.xml"
MEETING_TWO_OUT = "MeetingTwoOut.xml"
MEETING_TWO_OUT_COMMITMENTS = "MeetingTwoOutCommitments.xml"
MEETING_TWO_RANDOM_DATA = "pre-election-random-data.txt"

# third meeting
MEETING_THREE_IN = "MeetingThreeIn.xml"
MEETING_THREE_OUT = "MeetingThreeOut.xml"
MEETING_THREE_OUT_CODES = "MeetingThreeOutCodes.xml"

def go_provisional():
  # oh I feel dirty, but this is what happens when a new piece of the process is introduced without warning
  global MEETING_THREE_IN
  global MEETING_THREE_OUT
  global MEETING_THREE_OUT_CODES
  
  # third meeting with provisional ballots
  MEETING_THREE_IN = "MeetingThreeIn-Provisional-Manual.xml"
  MEETING_THREE_OUT = "MeetingThreeOut-Provisional-Manual.xml"
  MEETING_THREE_OUT_CODES = "MeetingThreeOutCodes-Provisional-Manual.xml"
  
def reset():
  # oh I feel dirty, but this is what happens when a new piece of the process is introduced without warning
  global MEETING_THREE_IN
  global MEETING_THREE_OUT
  global MEETING_THREE_OUT_CODES

  MEETING_THREE_IN = "MeetingThreeIn.xml"
  MEETING_THREE_OUT = "MeetingThreeOut.xml"
  MEETING_THREE_OUT_CODES = "MeetingThreeOutCodes.xml"

# fourth meeting
MEETING_FOUR_IN = "MeetingFourIn.xml"
MEETING_FOUR_OUT = "MeetingFourOut.xml"
MEETING_FOUR_RANDOM_DATA = "post-election-random-data.txt"

# contested ballots
CONTESTED_BALLOTS_REPLY = "ReplyToContestedCodes.xml"

# spoiled ballots
SPOILED_BALLOTS_CODES = "SpoiledBallotsCodes.xml"
SPOILED_BALLOTS_MIXNET = "SpoiledBallotsMixnet.xml"

# unused ballots
UNUSED_BALLOTS_CODES = "PrintAuditBallots.xml"
UNUSED_BALLOTS_MIXNET = "PrintAuditMixnet.xml"