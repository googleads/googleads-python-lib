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

"""This example gets all forecast adjustments for a traffic forecast segment."""

# Import appropriate modules from the client library.
from googleads import ad_manager

TRAFFIC_FORECAST_SEGMENT_ID = 'INSERT_FORECAST_SEGMENT_ID_HERE'


def main(client, traffic_forecast_segment_id):
  # Initialize the adjustment service.
  adjustment_service = client.GetService('AdjustmentService', version='v202211')

  # Create a statement to get forecast adjustments for a given traffic forecast
  # segment id.
  statement = ad_manager.StatementBuilder(version='v202211').Where(
      'trafficForecastSegmentId = :segmentId').WithBindVariable(
          'segmentId', traffic_forecast_segment_id)

  # Retrieve a small number of forecast adjustments at a time, paging
  # through until all forecast adjustments have been retrieved.
  while True:
    response = adjustment_service.getForecastAdjustmentsByStatement(
        statement.ToStatement())
    if 'results' in response and len(response['results']):
      for adjustment in response['results']:
        # Print out some information for each traffic adjustment.
        print('Forecast adjustment with id %d and name "%s" belonging to '
              'forecast segment %d was found.' %
              (adjustment['id'], adjustment['name'],
               adjustment['trafficForecastSegmentId']))
      statement.offset += statement.limit
    else:
      break

  print('\nNumber of results found: %s' % response['totalResultSetSize'])


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, int(TRAFFIC_FORECAST_SEGMENT_ID))
