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

"""This code example gets a delivery forecast for two existing line items.

To determine which line items exist, run get_all_line_items.py.

"""


# Import appropriate modules from the client library.
from googleads import dfp

# Set the line items to get forecasts for.
LINE_ITEM_ID_1 = 'INSERT_LINE_ITEM_ID_1_HERE'
LINE_ITEM_ID_2 = 'INSERT_LINE_ITEM_ID_2_HERE'


def main(client, line_item_id1, line_item_id2):
  # Initialize appropriate service.
  forecast_service = client.GetService('ForecastService', version='v201505')

  # Get forecast for line item.
  forecast = forecast_service.getDeliveryForecastByIds(
      [line_item_id1, line_item_id2], None)

  for single_forecast in forecast['lineItemDeliveryForecasts']:
    unit_type = single_forecast['unitType']
    print ('Forecast for line item %d:\n\t%d %s matched\n\t%d %s delivered\n\t'
           '%d %s predicted\n' % (
               single_forecast['lineItemId'], single_forecast['matchedUnits'],
               unit_type, single_forecast['deliveredUnits'], unit_type,
               single_forecast['predictedDeliveryUnits'], unit_type))


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, LINE_ITEM_ID_1, LINE_ITEM_ID_2)
