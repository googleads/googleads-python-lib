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

"""Retrieves available ad types and displays the name and ID for each type.


Tags: ad.getAdTypes
"""

__author__ = 'Joseph DiLallo'

# Import appropriate modules from the client library.
from googleads import dfa


def main(client):
  # Initialize appropriate service.
  ad_service = client.GetService(
      'ad', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Get ad types.
  results = ad_service.getAdTypes()

  # Display ad type names and IDs.
  if results:
    for ad_type in results:
      print ('Ad type with name \'%s\' and ID \'%s\' was found.'
             % (ad_type['name'], ad_type['id']))
  else:
    print 'No activity types found.'


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client)
