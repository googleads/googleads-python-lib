#!/usr/bin/python
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


"""Adds a price extension and associates it with an account.

Campaign targeting is also set usin the specified campaign ID. To get campaigns,
run get_campaigns.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

from googleads import adwords
from googleads import errors


CAMPAIGN_ID = 'INSERT_CAMPAIGN_ID_HERE'
MICROS_PER_DOLLAR = 1000000


def main(client, campaign_id):
  # Initialize appropriate service.
  customer_extension_setting_service = client.GetService(
      'CustomerExtensionSettingService', 'v201609')

  # To create a price extension, at least three table rows are needed.
  table_rows = [
      CreatePriceTableRow('Scrubs', 'Body Scrub, Salt Scrub',
                          'https://www.example.com/scrubs',
                          60 * MICROS_PER_DOLLAR, 'USD', 'PER_HOUR'),
      CreatePriceTableRow('Hair Cuts', 'Once a month',
                          'https://www.example.com/haircuts',
                          75 * MICROS_PER_DOLLAR, 'USD', 'PER_MONTH'),
      CreatePriceTableRow('Skin Care Package', 'Four times a month',
                          'https://www.examples.com/skincarepackage',
                          250 * MICROS_PER_DOLLAR, 'USD', 'PER_MONTH')
  ]

  # Create the price extension feed item.
  customer_extension_setting = {
      'extensionType': 'PRICE',
      'extensionSetting': {
          'extensions': [{
              'priceExtensionType': 'SERVICES',
              'trackingUrlTemplate': 'http://tracker.example.com/?u={lpurl}',
              'language': 'en',
              'campaignTargeting': {
                  'TargetingCampaignId': campaign_id
              },
              'scheduling': {
                  'feedItemSchedules': [
                      {
                          'dayOfWeek': 'SATURDAY',
                          'startHour': 10,
                          'startMinute': 'ZERO',
                          'endHour': 22,
                          'endMinute': 'ZERO'
                      },
                      {
                          'dayOfWeek': 'SUNDAY',
                          'startHour': 10,
                          'startMinute': 'ZERO',
                          'endHour': 18,
                          'endMinute': 'ZERO'
                      }
                  ]
              },
              'tableRows': table_rows,
              # Price qualifier is optional.
              'priceQualifier': 'FROM',
              'xsi_type': 'PriceFeedItem'
          }]
      }
  }

  # Create an operation to add the feed.
  operations = [{
      'operator': 'ADD',
      'operand': customer_extension_setting
  }]

  # Add the price extension.
  response = customer_extension_setting_service.mutate(operations)

  # Print the results.
  if 'value' in response:
    print ('Extension setting with type "%s" was added to your account.'
           % response['value'][0]['extensionType'])
  else:
    raise errors.GoogleAdsError('No extension settings were added.')


def CreatePriceTableRow(header, description, final_url, price_in_micros,
                        currency_code, price_unit):
  """Helper function to generate a single row of a price table.

  Args:
    header: A str containing the header text of this row.
    description: A str description of this row in the price table.
    final_url: A str containing the final URL after all cross domain redirects.
    price_in_micros: An int indicating the price of the given currency in
      micros.
    currency_code: A str indicating the currency code being used.
    price_unit: A str enum indicating the price unit for this row.

  Returns:
    A dictionary containing the contents of the generated price table row.
  """
  return {
      'header': header,
      'description': description,
      'finalUrls': {'urls': [final_url]},
      'price': {
          'money': {
              'microAmount': price_in_micros,
          },
          'currencyCode': currency_code
      },
      'priceUnit': price_unit,
      'xsi_type': 'PriceTableRow'
  }


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()
  main(adwords_client, CAMPAIGN_ID)
