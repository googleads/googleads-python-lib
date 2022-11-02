#!/usr/bin/env python
#
# Copyright 2020 Google LLC
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

"""This example creates a traffic forecast segment for all ad units in the U.S.
"""

import uuid

# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  # Initialize the adjustment service and the network service.
  adjustment_service = client.GetService('AdjustmentService', version='v202211')
  network_service = client.GetService('NetworkService', version='v202211')

  # Get the root ad unit id to target the whole site.
  current_network = network_service.getCurrentNetwork()
  root_ad_unit_id = current_network['effectiveRootAdUnitId']

  # Create inventory targeting.
  inventory_targeting = {
      'targetedAdUnits': [{
          'includeDescendants': True,
          'adUnitId': root_ad_unit_id
      }]
  }

  # Create targeting for United States traffic.
  geo_targeting = {
      'targetedLocations': [{
          'id': 2840
      }]
  }

  # Create traffic forecast segment object.
  segment = {
      'name': 'Forecast segment #%s' % uuid.uuid4(),
      'targeting': {
          'inventoryTargeting': inventory_targeting,
          'geoTargeting': geo_targeting
      }
  }

  # Create the traffic forecast segment on the server.
  segments = adjustment_service.createTrafficForecastSegments([segment])

  # Display the results.
  for segment in segments:
    print('Traffic forecast segment with id %d and %d forecast adjustments was '
          'created.' % (segment['id'],
                        segment['forecastAdjustmentCount']))


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
