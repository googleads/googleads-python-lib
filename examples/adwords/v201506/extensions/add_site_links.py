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

"""Adds sitelinks to a campaign using the CampaignExtensionSettingService.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Api: AdWordsOnly
"""


from datetime import datetime


from googleads import adwords
from googleads import errors
from pytz import timezone

CAMPAIGN_ID = 'INSERT_CAMPAIGN_ID_HERE'


def main(client, campaign_id):
  # Initialize appropriate services.
  campaign_extension_setting_service = client.GetService(
      'CampaignExtensionSettingService', version='v201506')
  customer_service = client.GetService('CustomerService', version='v201506')

  customer_tz = timezone(customer_service.get()['dateTimeZone'])
  time_fmt = '%s %s' % ('%Y%m%d %H%M%S', customer_tz)

  # Create the sitelinks
  sitelink1 = {
      'xsi_type': 'SitelinkFeedItem',
      'sitelinkText': 'Store Hours',
      'sitelinkFinalUrls': {'urls': ['http://www.example.com/storehours']}
  }

  # Show the Thanksgiving specials link only from 20 - 27 Nov.
  sitelink2 = {
      'xsi_type': 'SitelinkFeedItem',
      'sitelinkText': 'Thanksgiving Specials',
      'sitelinkFinalUrls': {'urls': ['http://www.example.com/thanksgiving']},
      # The time zone of the start and end date/times must match the time zone
      # of the customer.
      'startTime': datetime(datetime.now().year, 11, 20, 0, 0, 0, 0,
                            customer_tz).strftime(time_fmt),
      'endTime': datetime(datetime.now().year, 11, 27, 23, 59, 59, 59,
                          customer_tz).strftime(time_fmt)
  }

  # Show the wifi details primarily for high end mobile users.
  sitelink3 = {
      'xsi_type': 'SitelinkFeedItem',
      'sitelinkText': 'Wifi Available',
      'sitelinkFinalUrls': {'urls': ['http://www.example.com/mobile/wifi']},
      # See https://developers.google.com/adwords/api/docs/appendix/platforms
      # for device criteria IDs.
      'devicePreference': {'devicePreference': '30001'}
  }

  # Show the happy hours link only during Mon - Fri 6PM to 9PM.
  sitelink4 = {
      'xsi_type': 'SitelinkFeedItem',
      'sitelinkText': 'Happy hours',
      'sitelinkFinalUrls': {'urls': ['http://www.example.com/happyhours']},
      'scheduling': {
          'feedItemSchedules': [
              {
                  'dayOfWeek': day,
                  'startHour': '18',
                  'startMinute': 'ZERO',
                  'endHour': '21',
                  'endMinute': 'ZERO'
              } for day in ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY',
                            'FRIDAY']
          ]
      }
  }

  # Create your Campaign Extension Settings. This associates the sitelinks
  # to your campaign.
  campaign_extension_setting = {
      'campaignId': campaign_id,
      'extensionType': 'SITELINK',
      'extensionSetting': {
          'extensions': [sitelink1, sitelink2, sitelink3, sitelink4]
      }
  }

  operation = {
      'operator': 'ADD',
      'operand': campaign_extension_setting
  }

  # Add the extensions.
  response = campaign_extension_setting_service.mutate([operation])

  if 'value' in response:
    print ('Extension setting with type "%s" was added to campaignId "%d".' %
           (response['value'][0]['extensionType'],
            response['value'][0]['campaignId']))
  else:
    raise errors.GoogleAdsError('No extension settings were added.')


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, CAMPAIGN_ID)
