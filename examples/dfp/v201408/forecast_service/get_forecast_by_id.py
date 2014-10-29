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

"""This code example gets a forecast for an existing line item.

To determine which line items exist, run get_all_line_items.py."""

__author__ = ('Nicholas Chen',
              'Joseph DiLallo')

# Import appropriate modules from the client library.
from googleads import dfp

# Set the line item to get a forecast for.
LINE_ITEM_ID = 'INSERT_LINE_ITEM_ID'


def main(client, line_item_id):
  # Initialize appropriate service.
  forecast_service = client.GetService('ForecastService', version='v201408')

  # Get forecast for line item.
  forecast = forecast_service.getForecastById(line_item_id)
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

  if 'possibleUnits' in forecast:
    possible_percent = (long(forecast['possibleUnits'])/(matched * 1.0)) * 100
    print '%s%% %s possible' % (possible_percent, forecast['unitType'].lower())

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, LINE_ITEM_ID)
