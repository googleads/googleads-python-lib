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
"""This example gets all highly requested suggested ad units.
"""

# Import appropriate modules from the client library.
from googleads import ad_manager

NUM_REQUESTS = 'INSERT_NUM_REQUESTS_HERE'


def main(client, num_requests):
  # Initialize appropriate service.
  suggested_ad_unit_service = client.GetService(
      'SuggestedAdUnitService', version='v202505')
  # Create a statement to select suggested ad units.
  statement = (ad_manager.StatementBuilder(version='v202505')
               .Where('numRequests >= :numRequests')
               .WithBindVariable('numRequests', int(num_requests)))

  # Retrieve a small amount of suggested ad units at a time, paging
  # through until all suggested ad units have been retrieved.
  while True:
    response = suggested_ad_unit_service.getSuggestedAdUnitsByStatement(
        statement.ToStatement())
    if 'results' in response and len(response['results']):
      for suggested_ad_unit in response['results']:
        # Print out some information for each suggested ad unit.
        print(
            'Suggested ad unit with ID "%s" and num requests "%d" was found.\n'
            % (suggested_ad_unit['id'], suggested_ad_unit['numRequests']))
      statement.offset += statement.limit
    else:
      break

  print('\nNumber of results found: %s' % response['totalResultSetSize'])


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, NUM_REQUESTS)
