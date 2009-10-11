"""
filenames for individual audit files

Ben Adida
ben@adida.net
2009-10-10
"""

# first meeting
MEETING_ONE_IN = "MeetingOneIn.xml"
MEETING_ONE_OUT = "MeetingOneOut.xml"
ELECTION_SPEC = "ElectionSpec.xml"
PARTITIONS = "partitions.xml"

def file_in_dir(dir, file):
  return dir + "/" + file