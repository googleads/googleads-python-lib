#!/usr/bin/env python
#
# Copyright 2016 Google Inc. All Rights Reserved.
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

"""Imports offline conversion values for calls related to ads in your account.

To set up a conversion tracker, run the add_conversion_tracker.py example.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

from googleads import adwords


CALLER_ID = 'INSERT_CALLER_ID_HERE'
# For times use the format yyyyMMdd HHmmss tz. For more details on formats, see:
# https://developers.google.com/adwords/api/docs/appendix/codes-formats#date-and-time-formats
# For time zones, see:
# https://developers.google.com/adwords/api/docs/appendix/codes-formats#timezone-ids
CALL_START_TIME = 'INSERT_CALL_START_TIME'
CONVERSION_NAME = 'INSERT_CONVERSION_NAME_HERE'  # Name of conversion tracker.
CONVERSION_TIME = 'INSERT_CONVERSION_TIME_HERE'
CONVERSION_VALUE = 'INSERT_CONVERSION_VALUE_HERE'


def main(client, caller_id, call_start_time, conversion_name, conversion_time,
         conversion_value):
  # Initialize appropriate services.
  occ_feed_service = client.GetService(
      'OfflineCallConversionFeedService', version='v201702')

  # Associate offline call conversions with the existing named conversion
  # tracker. If this tracker was newly created, it may be a few hours before it
  # can accept conversions.
  feed = {
      'callerId': caller_id,
      'callStartTime': call_start_time,
      'conversionName': conversion_name,
      'conversionTime': conversion_time,
      'conversionValue': conversion_value,
  }

  occ_operations = [{'operator': 'ADD', 'operand': feed}]

  occ_response = occ_feed_service.mutate(occ_operations)
  values = occ_response['value']

  if values:
    for occ_feed in values:
      print ('Uploaded offline call conversion value of "%s" for caller ID '
             '"%s".\n' % (occ_feed['conversionName'], occ_feed['callerId']))
  else:
    print 'No offline call conversions were added.'


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, CALLER_ID, CALL_START_TIME, CONVERSION_NAME,
       CONVERSION_TIME, CONVERSION_VALUE)
