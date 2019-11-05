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

"""This example gets a forecast for a prospective line item.

The prospective line item targets the entire network. The targeting can be
modified to determine forecasts for other criteria such as custom criteria
targeting (in addition to targeting the whole network). See
create_line_items.py for an example of how to create more complex targeting.

"""


import datetime

# Import appropriate modules from the client library.
from googleads import ad_manager
import pytz

# Set the ID of the advertiser (company) to forecast for. Setting an advertiser
# will cause the forecast to apply the appropriate unified blocking rules.
ADVERTISER_ID = 'INSERT_ADVERTISER_ID_HERE'


def main(client, advertiser_id):
  # Initialize appropriate service.
  forecast_service = client.GetService('ForecastService', version='v201911')
  network_service = client.GetService('NetworkService', version='v201911')

  # get the root ad unit ID to target the entire network.
  root_ad_unit_id = network_service.getCurrentNetwork()['effectiveRootAdUnitId']

  now_datetime = datetime.datetime.now(tz=pytz.timezone('America/New_York'))
  end_datetime = now_datetime + datetime.timedelta(days=5)

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
              },
              'isAmpOnly': True,
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
      'endDateTime': end_datetime,
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
      'lineItem': line_item,
      'advertiserId': advertiser_id
  }

  # Set forecasting options.
  forecast_options = {
      'includeContendingLineItems': True,
      # The field includeTargetingCriteriaBreakdown can only be set if
      # breakdowns are not manually specified.
      # 'includeTargetingCriteriaBreakdown': True,
      'breakdown': {
          'timeWindows': [
              now_datetime,
              now_datetime + datetime.timedelta(days=1),
              now_datetime + datetime.timedelta(days=2),
              now_datetime + datetime.timedelta(days=3),
              now_datetime + datetime.timedelta(days=4),
              end_datetime
          ],
          'targets': [
              {
                  # Optional, the name field is only used to identify this
                  # breakdown in the response.
                  'name': 'United States',
                  'targeting': {
                      'inventoryTargeting': {
                          'targetedAdUnits': [
                              {
                                  'includeDescendants': True,
                                  'adUnitId': root_ad_unit_id,
                              }
                          ]
                      },
                      'geoTargeting': {
                          'targetedLocations': [
                              {
                                  'id': '2840',
                                  'displayName': 'US'
                              }
                          ]
                      }
                  }
              },
              {
                  # Optional, the name field is only used to identify this
                  # breakdown in the response.
                  'name': 'Geneva',
                  'targeting': {
                      'inventoryTargeting': {
                          'targetedAdUnits': [
                              {
                                  'includeDescendants': True,
                                  'adUnitId': root_ad_unit_id,
                              }
                          ]
                      },
                      'geoTargeting': {
                          'targetedLocations': [
                              {
                                  'id': '20133',
                                  'displayName': 'Geneva'
                              }
                          ]
                      }
                  }
              }
          ]
      }
  }

  # Get forecast.
  forecast = forecast_service.getAvailabilityForecast(
      prospective_line_item, forecast_options)
  matched = forecast['matchedUnits']
  available = forecast['availableUnits']
  possible = forecast['possibleUnits'] if 'possibleUnits' in forecast else None
  unit_type = forecast['unitType'].lower()

  available_percent_overall, possible_percent_overall = CalculateForecastStats(
      matched, available, possible)

  contending_line_items = getattr(forecast, 'contendingLineItems', [])

  # Display results.
  print('%s %s matched overall.' % (matched, unit_type))
  print('%s%% %s available overall.' % (available_percent_overall, unit_type))
  print('%d contending line items overall.' % len(contending_line_items))
  if possible:
    print('%s%% %s possible overall.' % (possible_percent_overall, unit_type))

  if 'breakdowns' in forecast and len(forecast['breakdowns']):
    for breakdown in forecast['breakdowns']:
      print('For breakdown time period %s - %s:' % (
          FormatSOAPDateTime(breakdown['startTime']),
          FormatSOAPDateTime(breakdown['endTime'])))
      for breakdown_entry in breakdown['breakdownEntries']:
        matched = breakdown_entry['forecast']['matched']
        available = breakdown_entry['forecast']['available']
        possible = (breakdown_entry['forecast']['possible']
                    if 'possible' in breakdown_entry['forecast'] else None)
        name = breakdown_entry['name'] if 'name' in breakdown_entry else None
        if name:
          print('\tFor targeting breakdown named \'%s\'' % name)
        available_percent, possible_percent = CalculateForecastStats(
            matched, available, possible)
        print('\t\t%s %s matched.' % (matched, unit_type))
        print('\t\t%s%% %s available.' % (available_percent, unit_type))
        if possible:
          print('\t\t%s%% %s possible.' % (possible_percent, unit_type))


def FormatSOAPDateTime(value):
  """Format a SOAP DateTime object for printing.

  Args:
    value: The DateTime object to format.

  Returns:
    A string representing the value.
  """
  value_date = value['date']
  return '%s-%s-%s %s:%s:%s (%s)' % (
      value_date['year'], value_date['month'], value_date['day'],
      value['hour'], value['minute'], value['second'], value['timeZoneId'])


def CalculateForecastStats(matched, available, possible=None):
  """Calculate forecast percentage stats.

  Args:
    matched: The number of matched impressions.
    available: The number of available impressions.
    possible: The optional number of possible impressions.

  Returns:
    The percentage of impressions that are available and possible.
  """
  if matched > 0:
    available_percent = (float(available) / matched) * 100.
  else:
    available_percent = 0

  if possible is not None:
    if matched > 0:
      possible_percent = (possible/float(matched)) * 100.
    else:
      possible_percent = 0
  else:
    possible_percent = None

  return available_percent, possible_percent


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, ADVERTISER_ID)
