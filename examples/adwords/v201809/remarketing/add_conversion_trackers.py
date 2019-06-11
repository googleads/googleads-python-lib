#!/usr/bin/env python
#
# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This example adds AdWords conversion trackers.

Adds an AdWords conversion tracker and an upload conversion tracker.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


import uuid
from googleads import adwords


def main(client):
  # Initialize appropriate service.
  conversion_tracker_service = client.GetService(
      'ConversionTrackerService', version='v201809')

  # Create an AdWords conversion tracker.
  adwords_conversion_tracker = {
      'xsi_type': 'AdWordsConversionTracker',
      'name': 'Earth to Mars Cruises Conversion #%s' % uuid.uuid4(),
      'category': 'DEFAULT',
      # Optional fields.
      'status': 'ENABLED',
      'viewthroughLookbackWindow': '15',
      'defaultRevenueValue': '23.41',
      'alwaysUseDefaultRevenueValue': 'true'
  }

  upload_conversion = {
      'xsi_type': 'UploadConversion',
      'name': 'Upload Conversion #%s' % uuid.uuid4(),
      # Optional fields.
      # Set an appropriate category. This will be set to DEFAULT if not
      # specified.
      'category': 'LEAD',
      'viewthroughLookbackWindow': '30',
      'ctcLookbackWindow': '90',
      # Set the default currency code to use for conversions that do
      # not specify a conversion currency. This must be an ISO 4217 3-character
      # code such as "EUR" or "USD".
      # If this field is not set, AdWords will use the account's currency.
      'defaultRevenueCurrencyCode': 'EUR',
      # Set the default revenue value to use for conversions that do not specify
      # a converison value. Note that this value should NOT be in micros.
      'defaultRevenueValue': '2.50',
      # To upload fractional conversion credits, mark the upload conversion as
      # externally attributed. To learn more about importing externally
      # attributed conversions, see:
      # https://developers.google.com/adwords/api/docs/guides/conversion-tracking#importing_externally_attributed_conversions
      # 'isExternallyAttributed': 'true'
  }

  # Construct operations.
  operations = [{
      'operator': 'ADD',
      'operand': conversion_tracker
  } for conversion_tracker in [adwords_conversion_tracker, upload_conversion]]

  # Add the conversions.
  conversion_trackers = conversion_tracker_service.mutate(operations)

  # Display results.
  for conversion_tracker in conversion_trackers['value']:
    print('Conversion with ID "%d", name "%s", status "%s", and category '
          '"%s" was added.'
          % (conversion_tracker['id'], conversion_tracker['name'],
              conversion_tracker['status'], conversion_tracker['category']))
    if (conversion_tracker['ConversionTracker.Type']
        == 'AdWordsConversionTracker'):
      print('Google global site tag:\n%s\n\n'
            % conversion_tracker['googleGlobalSiteTag'])
      print('Google event snippet:\n%s\n\n'
            % conversion_tracker['googleEventSnippet'])


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client)
