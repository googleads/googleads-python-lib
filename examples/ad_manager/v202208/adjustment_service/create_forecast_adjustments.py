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

"""This example creates a forecast adjustment for New Year's Day traffic."""

import datetime
import uuid

# Import appropriate modules from the client library.
from googleads import ad_manager

TRAFFIC_FORECAST_SEGMENT_ID = 'INSERT_TRAFFIC_FORECAST_SEGMENT_ID_HERE'


def main(client, traffic_forecast_segment_id):
  # Initialize the adjustment service.
  adjustment_service = client.GetService('AdjustmentService', version='v202208')

  # Create a new forecast adjustment for New Year's Day traffic.
  this_new_years = datetime.date(datetime.date.today().year, 1, 1)
  next_new_years = datetime.date(datetime.date.today().year + 1, 1, 1)

  forecast = {
      'name': 'Forecast adjustment #%s' % uuid.uuid4(),
      'trafficForecastSegmentId': traffic_forecast_segment_id,
      'dateRange': {
          'startDate': next_new_years,
          'endDate': next_new_years
      },
      'status': 'ACTIVE',
      'volumeType': 'HISTORICAL_BASIS_VOLUME',
      'historicalBasisVolumeSettings': {
          'useParentTrafficForecastSegmentTargeting': True,
          'historicalDateRange': {
              'startDate': this_new_years,
              'endDate': this_new_years
          },
          'multiplierMilliPercent': 110000
      }
  }

  forecasts = adjustment_service.createForecastAdjustments([forecast])

  for forecast in forecasts:
    print('Forecast adjustment with id %d and name "%s" was created.' % (
        forecast['id'], forecast['name']
    ))

if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, TRAFFIC_FORECAST_SEGMENT_ID)
