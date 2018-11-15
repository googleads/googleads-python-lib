#!/usr/bin/env python
#
# Copyright 2015 Google Inc. All Rights Reserved.
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

"""This code example updates ad unit sizes by adding a banner ad size.

To determine which ad units exist, run get_all_ad_units.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import ad_manager


# Set the ID of the ad unit to get.
AD_UNIT_ID = 'INSERT_AD_UNIT_ID_HERE'


def main(client, ad_unit_id):
  # Initialize appropriate service.
  inventory_service = client.GetService('InventoryService', version='v201805')

  # Create a statement to select a single ad unit by ID.
  statement = (ad_manager.StatementBuilder(version='v201805')
               .Where('id = :id')
               .WithBindVariable('id', ad_unit_id))

  # Get ad units by statement.
  response = inventory_service.getAdUnitsByStatement(
      statement.ToStatement())

  # Add the size 468x60 to the ad unit.
  ad_unit_size = {
      'size': {
          'width': '468',
          'height': '60'
      },
      'environmentType': 'BROWSER'
  }

  if 'results' in response and len(response['results']):
    updated_ad_units = []
    for ad_unit in response['results']:
      if 'adUnitSizes' not in ad_unit:
        ad_unit['adUnitSizes'] = []
      ad_unit['adUnitSizes'].append(ad_unit_size)
      updated_ad_units.append(ad_unit)

    # Update ad unit on the server.
    ad_units = inventory_service.updateAdUnits(updated_ad_units)

    # Display results.
    for ad_unit in ad_units:
      ad_unit_sizes = ['{%s x %s}' % (size['size']['width'],
                                      size['size']['height'])
                       for size in ad_unit['adUnitSizes']]
      print ('Ad unit with ID "%s", name "%s", and sizes [%s] was updated'
             % (ad_unit['id'], ad_unit['name'], ','.join(ad_unit_sizes)))


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, AD_UNIT_ID)
