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

"""This example displays activity groups names and IDs for a given advertiser.

To create an advertiser, run create_advertiser.py.

Tags: spotlight.getSpotlightActivityGroups
"""

__author__ = 'Joseph DiLallo'

# Import appropriate modules from the client library.
from googleads import dfa


ADVERTISER_ID = 'INSERT_ADVERTISER_ID_HERE'


def main(client, advertiser_id):
  # Initialize appropriate service.
  spotlight_service = client.GetService(
      'spotlight', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Set activity group search criteria structure and use advertiser ID as search
  # criteria.
  spotlight_activity_group_search_criteria = {
      'advertiserId': advertiser_id
  }

  # Get activity groups.
  results = spotlight_service.getSpotlightActivityGroups(
      spotlight_activity_group_search_criteria)

  # Display activity group names and IDs.
  if results['records']:
    for activity_group in results['records']:
      print ('Activity group with name \'%s\' and ID \'%s\' was found.'
             % (activity_group['name'], activity_group['id']))
  else:
    print 'No activity groups found for your criteria.'


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client, ADVERTISER_ID)
