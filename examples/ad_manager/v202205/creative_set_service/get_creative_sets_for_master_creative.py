#!/usr/bin/env python
#
# Copyright 2016 Google Inc. All Rights Reserved.
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
"""This example gets all creative sets for a master creative.
"""

# Import appropriate modules from the client library.
from googleads import ad_manager

MASTER_CREATIVE_ID = 'INSERT_MASTER_CREATIVE_ID_HERE'


def main(client, master_creative_id):
  # Initialize appropriate service.
  creative_set_service = client.GetService(
      'CreativeSetService', version='v202205')
  # Create a statement to select creative sets.
  statement = (ad_manager.StatementBuilder(version='v202205')
               .Where('masterCreativeId = :masterCreativeId')
               .WithBindVariable('masterCreativeId', master_creative_id))

  # Retrieve a small amount of creative sets at a time, paging
  # through until all creative sets have been retrieved.
  while True:
    response = creative_set_service.getCreativeSetsByStatement(
        statement.ToStatement())
    if 'results' in response and len(response['results']):
      for creative_set in response['results']:
        # Print out some information for each creative set.
        print('Creative set with ID "%d" and name "%s" was found.\n' %
              (creative_set['id'], creative_set['name']))
      statement.offset += statement.limit
    else:
      break

  print('\nNumber of results found: %s' % response['totalResultSetSize'])


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, MASTER_CREATIVE_ID)
