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

"""This example adds an AdWords conversion.

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
      'ConversionTrackerService', version='v201705')

  # Construct operations and add conversion_tracker.
  operations = [
      {
          'operator': 'ADD',
          'operand': {
              'xsi_type': 'AdWordsConversionTracker',
              'name': 'Mars cruise customers #%s' % uuid.uuid4(),
              'category': 'DEFAULT',
              'textFormat': 'HIDDEN',
              # Optional fields.
              'status': 'ENABLED',
              'viewthroughLookbackWindow': '15',
              'conversionPageLanguage': 'en',
              'backgroundColor': '#0000FF',
              'defaultRevenueValue': '23.41',
              'alwaysUseDefaultRevenueValue': 'true'
          }
      }
  ]
  conversion_trackers = conversion_tracker_service.mutate(operations)

  # Display results.
  for conversion_tracker in conversion_trackers['value']:
    print ('Conversion tracker with id "%s", name "%s", status "%s" '
           'and category "%s" and snippet \n"%s"\n was added.\n' %
           (conversion_tracker['id'], conversion_tracker['name'],
            conversion_tracker['status'], conversion_tracker['category'],
            conversion_tracker['snippet']))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client)
