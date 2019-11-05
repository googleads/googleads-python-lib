#!/usr/bin/env python
#
# Copyright 2019 Google LLC
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

"""This example adds or replaces a forecast adjustment.

The adjustment will affect 1920x1080 video traffic in the United States.
"""

import datetime

# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  # Initialize the adjustment service and the network service.
  adjustment_service = client.GetService('AdjustmentService', version='v201911')
  network_service = client.GetService('NetworkService', version='v201911')

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

  # Create geo targeting. When using geo targeting with the adjustment service,
  # only locations of type COUNTRY are supported. You can download the latest
  # geo targets at https://developers.google.com/ad-manager/api/geotargets.
  geo_targeting = {
      'targetedLocations': [{
          'id': 2840
      }]  # USA.
  }

  # Create ad unit size to define the slice of inventory affected by the
  # traffic adjustment.
  ad_unit_size = {
      'size': {
          'width': 1920,
          'height': 1080
      },
      'environmentType': 'VIDEO_PLAYER'
  }

  # Create a new historical adjustment targeting next year's January with 105%
  # of the traffic of this year's January.
  this_january = {
      'startDate': datetime.date(datetime.date.today().year, 1, 1),
      'endDate': datetime.date(datetime.date.today().year, 1, 31)
  }
  next_january = {
      'startDate': datetime.date(datetime.date.today().year + 1, 1, 1),
      'endDate': datetime.date(datetime.date.today().year + 1, 1, 31)
  }

  january_segment = {
      'basisType': 'HISTORICAL',
      'historicalAdjustment': {
          'targetDateRange': next_january,
          'referenceDateRange': this_january,
          'milliPercentMultiplier': 105000
      }
  }

  # Create a new absolute adjustment of 500,000 ad opportunities for Christmas
  # and 1,000,000 opportunities for Boxing Day of next year.
  christmas_day = datetime.date(datetime.date.today().year + 1, 12, 25)
  boxing_day = christmas_day + datetime.timedelta(days=1)
  holiday_range = {'startDate': christmas_day, 'endDate': boxing_day}

  holiday_segment = {
      'basisType': 'ABSOLUTE',
      'adjustmentTimeSeries': {
          'timeSeriesDateRange': holiday_range,
          'timeSeriesValues': [500000, 1000000],  # xsd:long[]
          'valuePeriodType': 'DAILY'
      }
  }

  # Create a new absolute adjustment of 900,000 ad opportunities for the first
  # week of September of next year.
  first_week_of_september = {
      'startDate': datetime.date(datetime.date.today().year + 1, 9, 1),
      'endDate': datetime.date(datetime.date.today().year + 1, 9, 7)
  }

  september_segment = {
      'basisType': 'ABSOLUTE',
      'adjustmentTimeSeries': {
          'timeSeriesDateRange': first_week_of_september,
          'timeSeriesValues': [900000],
          'valuePeriodType': 'CUSTOM'
      }
  }

  # Create traffic forecast adjustment object.
  adjustment_segments = [january_segment, holiday_segment, september_segment]
  adjustment = {
      'filterCriteria': {
          'targeting': {
              'inventoryTargeting': inventory_targeting,
              'geoTargeting': geo_targeting
          },
          'adUnitSizes': [ad_unit_size]
      },
      'forecastAdjustmentSegments': adjustment_segments
  }

  # Create or update the traffic adjustment for the given filter criteria on
  # the server.
  updated_adjustments = adjustment_service.updateTrafficAdjustments(
      [adjustment])

  # Display the results.
  for updated_adjustment in updated_adjustments:
    print('Traffic forecast adjustment with id %d and %d segments was '
          'created.' % (updated_adjustment['id'],
                        len(updated_adjustment['forecastAdjustmentSegments'])))


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
