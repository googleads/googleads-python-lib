#!/usr/bin/env python
#
# Copyright 2020, Google LLC
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

"""This example gets the forecasted run-of-network traffic data."""


import datetime

# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  # Initialize appropriate service.
  forecast_service = client.GetService('ForecastService', version='v202505')
  network_service = client.GetService('NetworkService', version='v202505')

  # get the root ad unit ID to target the entire network.
  root_ad_unit_id = network_service.getCurrentNetwork()['effectiveRootAdUnitId']

  # Create a start date that's 7 days in the past and an end date that's 7 days
  # in the future.
  today = datetime.date.today()
  start_date = today - datetime.timedelta(days=7)
  end_date = today + datetime.timedelta(days=7)

  # Create targeting.
  targeting = {
      'inventoryTargeting': {
          'targetedAdUnits': [
              {
                  'includeDescendants': True,
                  'adUnitId': root_ad_unit_id,
              }
          ]
      }
  }

  # Request the traffic forecast data.
  traffic_data = forecast_service.getTrafficData({
      'targeting': targeting,
      'requestedDateRange': {
          'startDate': start_date,
          'endDate': end_date
      }
  })

  # Display historical data.
  historical_time_series = traffic_data['historicalTimeSeries']
  if historical_time_series is None:
    print('No historical data to display.')
  else:
    historical_start_date, historical_end_date = GetDatesFromForecastTimeSeries(
        historical_time_series)

    print('Historical Data:')
    offset = 0
    current_date = historical_start_date
    while current_date <= historical_end_date:
      print('%s: %d' % (current_date.isoformat(),
                        historical_time_series['values'][offset]))
      offset += 1
      current_date = historical_start_date + datetime.timedelta(days=offset)

  # Display forecasted data.
  forecasted_time_series = traffic_data['forecastedTimeSeries']
  if forecasted_time_series is None:
    print('No forecasted data to display.')
  else:
    forecasted_start_date, forecasted_end_date = GetDatesFromForecastTimeSeries(
        forecasted_time_series)

    print('Forecasted Data:')
    offset = 0
    current_date = forecasted_start_date
    while current_date <= forecasted_end_date:
      print('%s: %d' % (current_date.isoformat(),
                        forecasted_time_series['values'][offset]))
      offset += 1
      current_date = forecasted_start_date + datetime.timedelta(days=offset)


def GetDatesFromForecastTimeSeries(time_series):
  """Creates datetime.date objects from a forecast time series object.

  Args:
    time_series: The forecast time series containing start and end date info.

  Returns:
    A tuple of datetime.date objects, the first representing the start date and
    the second representing the end date.
  """
  date_range = time_series['timeSeriesDateRange']
  start_date = datetime.date(
      date_range['startDate']['year'],
      date_range['startDate']['month'],
      date_range['startDate']['day']
  )
  end_date = datetime.date(
      date_range['endDate']['year'],
      date_range['endDate']['month'],
      date_range['endDate']['day']
  )
  return start_date, end_date


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
