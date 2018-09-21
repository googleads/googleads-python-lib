#!/usr/bin/env python
#
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This example adds a responsive search ad to a given ad group.

To get ad groups, run get_ad_groups.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

import uuid

from googleads import adwords


AD_GROUP_ID = 'INSERT_AD_GROUP_ID_HERE'
NUMBER_OF_ADS = 5


def main(client, ad_group_id):
  # Initialize appropriate service.
  ad_group_ad_service = client.GetService('AdGroupAdService', version='v201809')

  responsive_search_ad = {
      'xsi_type': 'AdGroupAd',
      'adGroupId': ad_group_id,
      'ad': {
          'xsi_type': 'ResponsiveSearchAd',
          'finalUrls': ['http://www.example.com/cruise'],
          'path1': 'all-inclusive',
          'path2': 'deals',
          'headlines': [{
              'asset': {
                  'xsi_type': 'TextAsset',
                  'assetText': 'Cruise to Mars # ' + str(uuid.uuid4())[:8]
              },
              'pinnedField': 'HEADLINE_1'
          }, {
              'asset': {
                  'xsi_type': 'TextAsset',
                  'assetText': 'Best Space Cruise Line',
              }
          }, {
              'asset': {
                  'xsi_type': 'TextAsset',
                  'assetText': 'Experience the Stars'
              }
          }],
          'descriptions': [{
              'asset': {
                  'xsi_type': 'TextAsset',
                  'assetText': 'Buy your tickets now.'
              }
          }, {
              'asset': {
                  'xsi_type': 'TextAsset',
                  'assetText': 'Visit the Red Planet',
              }
          }],
      },
      # Optional fields.
      'status': 'PAUSED'
  }

  # Create the operations.
  operations = [{
      'operator': 'ADD',
      'operand': responsive_search_ad
  }]

  # Create the ad on the server.
  ads = ad_group_ad_service.mutate(operations)

  # Display results.
  for ad in ads['value']:
    ad = ad['ad']
    print ('Ad of type "%s" with id "%d" was added.\n'
           'Headlines:\n%s\n'
           'Descriptions:\n%s'
           % (ad['Ad.Type'], ad['id'],
              '\n'.join(['\t%s (pinned to %s)' %
                         (headline['asset']['assetText'],
                          headline['pinnedField'])
                         for headline in ad['headlines']]),
              '\n'.join(['\t%s (pinned to %s)' %
                         (headline['asset']['assetText'],
                          headline['pinnedField'])
                         for headline in ad['descriptions']])))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, AD_GROUP_ID)
