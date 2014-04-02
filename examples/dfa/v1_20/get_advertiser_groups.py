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

"""Displays advertiser groups for the given search criteria.

Results are limited to the first 10 records.


The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: advertisergroup.getAdvertiserGroups
"""

__author__ = 'Joseph DiLallo'

# Import appropriate modules from the client library.
from googleads import dfa


def main(client):
  # Initialize appropriate service.
  advertiser_group_service = client.GetService(
      'advertisergroup', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Create advertiser group search criteria structure.
  advertiser_group_search_criteria = {
      'pageSize': '10'
  }

  # Get advertiser group record set.
  results = advertiser_group_service.getAdvertiserGroups(
      advertiser_group_search_criteria)

  # Display advertiser group names, IDs and advertiser count.
  if results['records']:
    for advertiser_group in results['records']:
      print ('Advertiser group with name \'%s\', ID \'%s\', containing %s'
             ' advertisers was found.' % (advertiser_group['name'],
                                          advertiser_group['id'],
                                          advertiser_group['advertiserCount']))
  else:
    print 'No advertiser groups found for your criteria.'


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client)
