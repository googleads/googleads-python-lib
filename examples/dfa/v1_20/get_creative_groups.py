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

"""Retrieves and displays available creative groups for a given advertiser.

To get an advertiser ID, run get_advertisers.py. Results are limited to the
first 10.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: creativegroup.getCreativeGroups
"""

__author__ = 'Joseph DiLallo'

# Import appropriate modules from the client library.
from googleads import dfa


ADVERTISER_ID = 'INSERT_ADVERTISER_ID_HERE'


def main(client, advertiser_id):
  # Initialize appropriate service.
  creative_group_service = client.GetService(
      'creativegroup', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Set up creative group search criteria structure.
  creative_group_search_criteria = {
      'advertiserIds': [advertiser_id],
  }

  # Get creatives groups for the selected criteria.
  results = creative_group_service.getCreativeGroups(
      creative_group_search_criteria)

  # Display creative group names, IDs, advertiser IDs, and group numbers.
  if results['records']:
    for creative_field_value in results['records']:
      print ('Creative group with name \'%s\', ID \'%s\', advertiser ID \'%s\','
             ' and group number \'%s\' was found.'
             % (creative_field_value['name'], creative_field_value['id'],
                creative_field_value['advertiserId'],
                creative_field_value['groupNumber']))
  else:
    print 'No creative groups found for your criteria.'


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client, ADVERTISER_ID)
