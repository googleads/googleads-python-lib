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

"""This code example gets all creative sets for a master creative.

To create creative sets, run create_creative_sets.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: CreativeSetService.getCreativeSetsByStatement
"""

__author__ = ('Nicholas Chen',
              'Joseph DiLallo')

# Import appropriate modules from the client library.
from googleads import dfp

MASTER_CREATIVE_ID = 'INSERT_MASTER_CREATIVE_ID_HERE'


def main(client, master_creative_id):
  # Initialize appropriate service.
  creative_set_service = client.GetService('CreativeSetService',
                                           version='v201408')

  # Create statement object to only select creative sets that have the given
  # master creative.
  values = [{
      'key': 'masterCreativeId',
      'value': {
          'xsi_type': 'NumberValue',
          'value': master_creative_id
      }
  }]
  query = 'WHERE masterCreativeId = :masterCreativeId'
  statement = dfp.FilterStatement(query, values)

  # Get creative sets by statement.
  while True:
    response = creative_set_service.getCreativeSetsByStatement(
        statement.ToStatement())
    if 'results' in response:
      # Display results.
      for creative_set in response['results']:
        print (('Creative set with ID \'%s\', master creative ID \'%s\', and '
                'companion creative IDs {%s} was found.')
               % (creative_set['id'], creative_set['masterCreativeId'],
                  ','.join(creative_set['companionCreativeIds'])))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, MASTER_CREATIVE_ID)
