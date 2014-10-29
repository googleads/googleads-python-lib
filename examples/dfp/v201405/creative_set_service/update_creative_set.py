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

"""This code example updates a creative set by adding a companion creative.

To determine which creative sets exist, run get_all_creative_sets.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: CreativeSetService.updateCreativeSet
      CreativeSetService.getCreativeSetsByStatement
"""

__author__ = ('Nicholas Chen',
              'Joseph DiLallo')

# Import appropriate modules from the client library.
from googleads import dfp

# Set the ID of the creative set to update.
CREATIVE_SET_ID = 'INSERT_CREATIVE_SET_ID_HERE'
COMPANION_CREATIVE_ID = 'INSERT_COMPANION_CREATIVE_ID_HERE'


def main(client, creative_set_id, companion_creative_id):
  # Initialize appropriate service.
  creative_set_service = client.GetService('CreativeSetService',
                                           version='v201405')

  # Create statement to select a single creative set by ID.
  values = [{
      'key': 'creativeSetId',
      'value': {
          'xsi_type': 'NumberValue',
          'value': creative_set_id
      }
  }]
  query = 'WHERE id = :creativeSetId'
  statement = dfp.FilterStatement(query, values)

  # Get creative set.
  response = creative_set_service.getCreativeSetsByStatement(
      statement.ToStatement())

  if 'results' in response:
    updated_created_sets = []
    for creative_set in response['results']:
      creative_set['companionCreativeIds'].append(companion_creative_id)
      updated_created_sets.append(creative_set)

    # Update the creative sets on the server.
    creative_sets = creative_set_service.updateCreativeSet(updated_created_sets)

    # Display results.
    for creative_set in creative_sets:
      print (('Creative set with ID \'%s\', master creative ID \'%s\', and '
              'companion creative IDs {%s} was updated.')
             % (creative_set['id'], creative_set['masterCreativeId'],
                ','.join(creative_set['companionCreativeIds'])))
  else:
    print 'No creative sets found to update.'

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, CREATIVE_SET_ID, COMPANION_CREATIVE_ID)
