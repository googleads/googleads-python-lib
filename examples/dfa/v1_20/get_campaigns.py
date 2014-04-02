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

"""This example gets existing campaigns based on a given search criteria.

Results are limited to the first 10.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: campaign.getCampaignsByCriteria
"""

__author__ = 'Joseph DiLallo'

# Import appropriate modules from the client library.
from googleads import dfa


def main(client):
  # Initialize appropriate service.
  campaign_service = client.GetService(
      'campaign', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Create campaign search criteria structure.
  page_number = 1
  campaign_search_criteria = {
      'pageSize': '100',
      'pageNumber': str(page_number)
  }

  while True:
    # Get campaign record set.
    results = campaign_service.getCampaignsByCriteria(
        campaign_search_criteria)

    # Display campaign names and IDs.
    if results['records']:
      for campaign in results['records']:
        print ('Campaign with name \'%s\' and ID \'%s\' was found.'
               % (campaign['name'], campaign['id']))
    page_number += 1
    campaign_search_criteria['pageNumber'] = str(page_number)
    if page_number > int(results['totalNumberOfPages']):
      break

  print 'Number of results found: %s' % results['totalNumberOfRecords']


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client)
