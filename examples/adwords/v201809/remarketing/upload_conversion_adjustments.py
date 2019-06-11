#!/usr/bin/env python
#
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Imports conversion adjustments for conversions that already exist.

To set up a conversion tracker, run the add_conversion_tracker.py example.

"""

from googleads import adwords


CONVERSION_NAME = 'INSERT_CONVERSION_NAME_HERE'

GCLID = 'INSERT_GCLID_HERE'

ADJUSTMENT_TYPE = 'INSERT_ADJUSTMENT_TYPE_HERE'

CONVERSION_TIME = 'INSERT_CONVERSION_TIME_HERE'

ADJUSTMENT_TIME = 'INSERT_ADJUSTMENT_TIME_HERE'

ADJUSTED_VALUE = 'INSERT_ADJUST_VALUE_HERE'


def main(client, conversion_name, gclid, adjustment_type, conversion_time,
         adjustment_time, adjusted_value):
  # Initialize appropriate services.
  offline_conversion_service = client.GetService(
      'OfflineConversionAdjustmentFeedService', version='v201809')

  # Associate conversion adjustments with the existing named conversion tracker.
  # The GCLID should have been uploaded before with a conversion.
  feed = {
      'xsi_type': 'GclidOfflineConversionAdjustmentFeed',
      'conversionName': conversion_name,
      'googleClickId': gclid,
      'conversionTime': conversion_time,
      'adjustmentType': adjustment_type,
      'adjustmentTime': adjustment_time,
      'adjustedValue': adjusted_value
  }

  offline_conversion_operation = {'operator': 'ADD', 'operand': feed}

  offline_conversion_response = offline_conversion_service.mutate(
      [offline_conversion_operation])

  new_feed = offline_conversion_response['value'][0]

  print('Uploaded offline conversion adjustment value of "%s" for Google '
        'Click ID "%s"' % (new_feed['adjustedValue'],
                           new_feed['googleClickId']))

if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, CONVERSION_NAME, GCLID, ADJUSTMENT_TYPE, CONVERSION_TIME,
       ADJUSTMENT_TIME, ADJUSTED_VALUE)
