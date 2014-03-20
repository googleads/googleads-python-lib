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

"""This code example gets all ad unit sizes defined in a network.

To create ad units, run create_ad_units.py

Tags: InventoryService.getAdUnitSizesByStatement
"""

__author__ = ('Nicholas Chen',
              'Joseph DiLallo')

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  inventory_service = client.GetService('InventoryService', version='v201403')
  statement = dfp.FilterStatement()

  # Get ad units by statement.
  while True:
    response = inventory_service.getAdUnitSizesByStatement(
        statement.ToStatement())
    if 'results' in response:
      # Display results.
      for ad_unit_size in response['results']:
        print ('Ad unit size of dimensions %s was found.' %
               (ad_unit_size['fullDisplayString']))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
