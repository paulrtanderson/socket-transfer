import sys

import os
import sys
import os
import argparse

def generate_file(size_in_mb, file_name):
  mega_byte = 1048576
  with open(file_name, 'wb') as file:
    file.write(os.urandom(size_in_mb*mega_byte))

#generate_file(10,"10mbfile")
"""
with open("largefile","rb") as file:
  print(str(file.read(1000)))
"""
generate_file(100,"100mbfile")
print("done")