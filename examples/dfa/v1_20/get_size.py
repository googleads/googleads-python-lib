#!/usr/bin/python
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This example gets the size ID for a given width and height.

Tags: size.getSize
"""

__author__ = 'Joseph DiLallo'

# Import appropriate modules from the client library.
from googleads import dfa


WIDTH = 'INSERT_WIDTH_HERE'
HEIGHT = 'INSERT_HEIGHT_HERE'


def main(client, width, height):
  # Initialize appropriate service.
  size_service = client.GetService(
      'size', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Create size search criteria.
  size_search_criteria = {
      'width': width,
      'height': height
  }

  # Get size.
  size_record_set = size_service.getSizes(size_search_criteria)

  # Display size ID.
  if size_record_set['records']:
    for size in size_record_set['records']:
      print 'Size id for \'%sx%s\' is \'%s\'.' % (width, height, size['id'])
  else:
    print 'No sizes found for your criteria.'


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client, WIDTH, HEIGHT)
