"""
Load up just election params
Scantegrity audit

Ben Adida
2009-10-31
"""

import base, data, filenames

partition_xml = base.file_in_dir(base.DATA_PATH, filenames.PARTITIONS, 'Partition File')
election_xml = base.file_in_dir(base.DATA_PATH, filenames.ELECTION_SPEC, 'Election Spec')
meeting_one_in_xml = base.file_in_dir(base.DATA_PATH, filenames.MEETING_ONE_IN, 'Meeting One In')

# parse
partition_info = data.PartitionInfo()
partition_info.parse(partition_xml)

election_spec = data.ElectionSpec(partition_info)
election_spec.parse(election_xml)

election = data.Election(election_spec)
election.parse(meeting_one_in_xml)
