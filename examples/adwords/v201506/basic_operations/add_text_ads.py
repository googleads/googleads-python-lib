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

"""This example adds several text ads to a given ad group.

To get ad_group_id, run get_ad_groups.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: AdGroupAdService.mutate
Api: AdWordsOnly
"""

__author__ = ('api.kwinter@gmail.com (Kevin Winter)'
              'Joseph DiLallo')

from googleads import adwords


AD_GROUP_ID = 'INSERT_AD_GROUP_ID_HERE'


def main(client, ad_group_id):
  # Initialize appropriate service.
  ad_group_ad_service = client.GetService('AdGroupAdService', version='v201506')

  # Construct operations and add ads.
  # If needed, you could specify an exemption request here, e.g.:
  # 'exemptionRequests': [{
  #     # This comes back in a PolicyViolationError.
  #     'key' {
  #         'policyName': '...',
  #         'violatingText': '...'
  #     }
  # }]
  operations = [
      {
          'operator': 'ADD',
          'operand': {
              'xsi_type': 'AdGroupAd',
              'adGroupId': ad_group_id,
              'ad': {
                  'xsi_type': 'TextAd',
                  'finalUrls': ['http://www.example.com'],
                  'displayUrl': 'example.com',
                  'description1': 'Visit the Red Planet in style.',
                  'description2': 'Low-gravity fun for everyone!',
                  'headline': 'Luxury Cruise to Mars'
              },
              # Optional fields.
              'status': 'PAUSED'
          }
      },
      {
          'operator': 'ADD',
          'operand': {
              'xsi_type': 'AdGroupAd',
              'adGroupId': ad_group_id,
              'ad': {
                  'xsi_type': 'TextAd',
                  'finalUrls': ['http://www.example.com'],
                  'displayUrl': 'example.com',
                  'description1': 'Enjoy your stay at Red Planet.',
                  'description2': 'Buy your tickets now!',
                  'headline': 'Luxury Cruise to Mars'
              }
          }
      }
  ]
  ads = ad_group_ad_service.mutate(operations)

  # Display results.
  for ad in ads['value']:
    print ('Ad with id \'%s\' and of type \'%s\' was added.'
           % (ad['ad']['id'], ad['ad']['Ad.Type']))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, AD_GROUP_ID)
