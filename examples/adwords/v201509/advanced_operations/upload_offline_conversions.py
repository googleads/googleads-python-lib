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

"""Imports offline conversion values for specific clicks into your account.

To get the Google Click ID for a click, run a CLICK_PERFORMANCE_REPORT.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


from googleads import adwords


CONVERSION_NAME = 'INSERT_CONVERSION_NAME_HERE'
# Your click ID must be less than 30 days old.
CLICK_ID = 'INSERT_GOOGLE_CLICK_ID_HERE'
# The conversion time must be more recent than the time of the click.
CONVERSION_TIME = 'INSERT_CONVERSION_TIME_HERE'
CONVERSION_VALUE = 'INSERT_CONVERSION_VALUE_HERE'


def main(client, conversion_name, click_id, conversion_time, conversion_value):
  # Initialize appropriate services.
  conversion_tracker_service = client.GetService('ConversionTrackerService',
                                                 version='v201509')

  offline_conversion_feed_service = client.GetService(
      'OfflineConversionFeedService', version='v201509')

  # Once created, this entry will be visible under
  # Tools and Analysis->Conversion and will have "Source = Import".
  upload_conversion = {
      'xsi_type': 'UploadConversion',
      'category': 'PAGE_VIEW',
      'name': conversion_name,
      'viewthroughLookbackWindow': '30',
      'ctcLookbackWindow': '90'
  }

  upload_conversion_operation = {
      'operator': 'ADD',
      'operand': upload_conversion
  }

  response = conversion_tracker_service.mutate(
      [upload_conversion_operation])
  new_upload_conversion = response['value']

  print ('New upload conversion type with name \'%s\' and ID \'%s\' was '
         'created.' % (new_upload_conversion['name'],
                       new_upload_conversion['id']))

  # Associate offline conversions with the upload conversion we created.
  feed = {
      'conversionName': conversion_name,
      'conversionTime': conversion_time,
      'conversionValue': conversion_value,
      'googleClickId': click_id
  }

  offline_conversion_operation = {
      'operator': 'ADD',
      'operand': feed
  }

  offline_conversion_response = offline_conversion_feed_service.mutate(
      [offline_conversion_operation])
  new_feed = offline_conversion_response['value']

  print ('Uploaded offline conversion value of \'%s\' for Google Click ID '
         '\'%s\' to \'%s\'.' % (new_feed['conversionValue'],
                                new_feed['googleClickId'],
                                new_feed['conversionName']))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, CONVERSION_NAME, CLICK_ID, CONVERSION_TIME,
       CONVERSION_VALUE)
