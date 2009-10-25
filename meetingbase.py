"""
The core of every meeting verification

not called directly

data path should NOT have a trailing slash
"""

from filenames import *
from data import *
import sys
from xml.etree import ElementTree

DATA_PATH = sys.argv[1] or "testdata"

FINGERPRINTS = []

def add_fingerprint(filename, hash_value):
  FINGERPRINTS.append([filename, hash_value])

def fingerprint_report():
  report = ""
  for filename, fingerprint in FINGERPRINTS:
    report += filename + ": " + fingerprint + "\n"
  return report

##
## loading files and adding fingerprints
##

def file_in_dir(dir, file, filename):
  path = dir + "/" + file

  f = open(path, "r")
  contents = f.read()
  f.close()
  
  add_fingerprint(filename, hashlib.sha1(contents).hexdigest())
  return ElementTree.fromstring(contents)
