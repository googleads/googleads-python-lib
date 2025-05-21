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
"""This example gets all ad units.
"""

# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  # Initialize appropriate service.
  ad_unit_service = client.GetService('InventoryService', version='v202505')

  # Create a statement to select ad units.
  statement = ad_manager.StatementBuilder(version='v202505')

  # Retrieve a small amount of ad units at a time, paging
  # through until all ad units have been retrieved.
  while True:
    response = ad_unit_service.getAdUnitsByStatement(statement.ToStatement())
    if 'results' in response and len(response['results']):
      for ad_unit in response['results']:
        # Print out some information for each ad unit.
        print('Ad unit with ID "%s" and name "%s" was found.\n' %
              (ad_unit['id'], ad_unit['name']))
      statement.offset += statement.limit
    else:
      break

  print('\nNumber of results found: %s' % response['totalResultSetSize'])


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
