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

"""This code example gets all child ad units of the effective root ad unit.

To create ad units, run create_ad_units.py

Tags: InventoryService.getAdUnitsByStatement
"""

__author__ = ('Nicholas Chen',
              'Joseph DiLallo')

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  inventory_service = client.GetService('InventoryService', version='v201403')
  network_service = client.GetService('NetworkService', version='v201403')

  root_id = network_service.getCurrentNetwork()['effectiveRootAdUnitId']

  # Create a statement to select the children of the effective root ad unit.
  values = [{
      'key': 'id',
      'value': {
          'xsi_type': 'TextValue',
          'value': root_id
      }
  }]
  query = 'WHERE parentId = :id'
  statement = dfp.FilterStatement(query, values)

  # Get ad units by statement.
  while True:
    response = inventory_service.getAdUnitsByStatement(
        statement.ToStatement())
    if 'results' in response:
      # Display results.
      for ad_unit in response['results']:
        print ('Ad unit with ID \'%s\' and name \'%s\' was found.'
               % (ad_unit['id'], ad_unit['name']))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
