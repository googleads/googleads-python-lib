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

"""Retrieves and displays available creative fields for a given string.

Results are limited to the first 10.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import dfa


ADVERTISER_ID = 'INSERT_ADVERTISER_ID_HERE'


def main(client, advertiser_id):
  # Initialize appropriate service.
  creative_field_service = client.GetService(
      'creativefield', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Set up creative field search criteria structure.
  creative_field_search_criteria = {
      'advertiserIds': [advertiser_id],
      'pageSize': '10'
  }

  # Get creative fields for the selected criteria.
  results = creative_field_service.getCreativeFields(
      creative_field_search_criteria)

  # Display creative field names, IDs, advertiser IDs, and number of values.
  if results['records']:
    for creative_field in results['records']:
      print ('Creative field with name \'%s\', ID \'%s\', advertiser ID \'%s\','
             ' and containing \'%s\' values was found.'
             % (creative_field['name'], creative_field['id'],
                creative_field['advertiserId'],
                creative_field['totalNumberOfValues']))
  else:
    print 'No creative fields found for your criteria.'


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client, ADVERTISER_ID)
