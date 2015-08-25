#!/usr/bin/python
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

"""This example gets a forecast for a prospective line item.

The prospective line item targets the entire network. The targeting can be
modified to determine forecasts for other criteria such as custom criteria
targeting (in addition to targeting the whole network). See
create_line_items.py for an example of how to create more complex targeting.

"""


from datetime import date

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  forecast_service = client.GetService('ForecastService', version='v201502')
  network_service = client.GetService('NetworkService', version='v201502')

  # get the root ad unit ID to target the entire network.
  root_ad_unit_id = network_service.getCurrentNetwork()['effectiveRootAdUnitId']

  # Create prospective line item.
  line_item = {
      'targeting': {
          'inventoryTargeting': {
              'targetedAdUnits': [
                  {
                      'includeDescendants': True,
                      'adUnitId': root_ad_unit_id,
                  }
              ]
          }
      },
      'creativePlaceholders': [
          {
              'size': {
                  'width': '300',
                  'height': '250'
              }
          },
          {
              'size': {
                  'width': '120',
                  'height': '600'
              }
          }
      ],
      'lineItemType': 'SPONSORSHIP',
      'startDateTimeType': 'IMMEDIATELY',
      'endDateTime': {
          'date': {
              'year': str(date.today().year + 1),
              'month': '9',
              'day': '30'
          },
          'hour': '0',
          'minute': '0',
          'second': '0',
          'timeZoneID': 'America/New_York'
      },
      'costType': 'CPM',
      'costPerUnit': {
          'currencyCode': 'USD',
          'microAmount': '2000000'
      },
      'primaryGoal': {
          'units': '50',
          'unitType': 'IMPRESSIONS',
          'goalType': 'DAILY'
      },
      'contractedUnitsBought': '100',
      'creativeRotationType': 'EVEN',
      'discountType': 'PERCENTAGE',
  }

  prospective_line_item = {
      'lineItem': line_item
  }

  # Set forecasting options.
  forecast_options = {
      'includeContendingLineItems': True,
      'includeTargetingCriteriaBreakdown': True,
  }

  # Get forecast.
  forecast = forecast_service.getAvailabilityForecast(
      prospective_line_item, forecast_options)
  matched = long(forecast['matchedUnits'])
  available_percent = (((long(forecast['availableUnits'])/
                         (matched * 1.0)) * 100)
                       if matched != 0 else 0)
  contending_line_items = ([] if 'contendingLineItems' not in forecast
                           else forecast['contendingLineItems'])

  # Display results.
  print '%s %s matched.' % (matched, forecast['unitType'].lower())
  print '%s%% %s available.' % (available_percent, forecast['unitType'].lower())
  print '%d contending line items.' % len(contending_line_items)

  if 'possibleUnits' in forecast and matched:
    possible_percent = (long(forecast['possibleUnits'])/(matched * 1.0)) * 100
    print '%s%% %s possible' % (possible_percent, forecast['unitType'].lower())

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
