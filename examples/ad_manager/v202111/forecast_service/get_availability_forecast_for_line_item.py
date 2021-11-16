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

"""This code example gets an availability forecast for an existing line item.

To determine which line items exist, run get_all_line_items.py.

"""


# Import appropriate modules from the client library.
from googleads import ad_manager

# Set the line item to get a forecast for.
LINE_ITEM_ID = 'INSERT_LINE_ITEM_ID_HERE'


def main(client, line_item_id):
  # Initialize appropriate service.
  forecast_service = client.GetService('ForecastService', version='v202111')

  # Set forecasting options.
  forecast_options = {
      'includeContendingLineItems': True,
      'includeTargetingCriteriaBreakdown': True,
  }

  # Get forecast for line item.
  forecast = forecast_service.getAvailabilityForecastById(
      line_item_id, forecast_options)
  matched = int(forecast['matchedUnits'])
  available_units = int(forecast['availableUnits'])

  if matched > 0:
    available_percent = (float(available_units) / matched) * 100.
  else:
    available_percent = 0

  contending_line_items = getattr(forecast, 'contentingLineItems', [])

  # Display results.
  print('%s %s matched.' % (matched, forecast['unitType'].lower()))
  print('%s%% %s available.' % (
      available_percent, forecast['unitType'].lower()))
  print('%d contending line items.' % len(contending_line_items))

  if 'possibleUnits' in forecast and matched:
    possible_percent = (int(forecast['possibleUnits'])/float(matched)) * 100.
    print('%s%% %s possible' % (possible_percent, forecast['unitType'].lower()))

if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, LINE_ITEM_ID)
