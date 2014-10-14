#!/usr/bin/python
#
# Copyright 2013 Google Inc. All Rights Reserved.
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

"""This example adds several third party ads to a given ad group.

To get an ad_group_id, run get_ad_groups.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: AdGroupAdService.mutate
"""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

import uuid

from googleads import adwords


AD_GROUP_ID = 'INSERT_AD_GROUP_ID_HERE'


def main(client, ad_group_id):
  # Initialize appropriate service.
  ad_group_ad_service = client.GetService('AdGroupAdService', version='v201409')

  # Construct operations and add ads.
  operations = [
      {
          'operator': 'ADD',
          'operand': {
              'xsi_type': 'AdGroupAd',
              'adGroupId': ad_group_id,
              'ad': {
                  'xsi_type': 'ThirdPartyRedirectAd',
                  'name': 'Example third party ad #%s' % uuid.uuid4(),
                  'url': 'http://www.example.com',
                  'dimensions': {
                      'width': '300',
                      'height': '250'
                  },
                  # This field normally contains the javascript ad tag.
                  'snippet': ('<img src="http://www.google.com/intl/en/adwords/'
                              'select/images/samples/inline.jpg"/>'),
                  'certifiedVendorFormatId': '232',
                  'isCookieTargeted': 'false',
                  'isUserInterestTargeted': 'false',
                  'isTagged': 'false',
                  'richMediaAdType': 'STANDARD',
                  'expandingDirections': ['EXPANDING_UP', 'EXPANDING_DOWN'],
                  'adAttributes': ['ROLL_OVER_TO_EXPAND']
              }
          }
      },
      {
          'operator': 'ADD',
          'operand': {
              'xsi_type': 'AdGroupAd',
              'adGroupId': ad_group_id,
              'ad': {
                  'xsi_type': 'ThirdPartyRedirectAd',
                  'name': 'Example third party ad #%s' % uuid.uuid4(),
                  'url': 'http://www.example.com',
                  'adDuration': '15000',
                  'sourceUrl': ('http://ad.doubleclick.net/pfadx/N270.126913.'
                                '6102203221521/B3876671.21;dcadv=2215309;'
                                'sz=0x0;ord=%5btimestamp%5d;dcmt=text/xml'),
                  'certifiedVendorFormatId': '303',
                  'richMediaAdType': 'IN_STREAM_VIDEO'
              }
          }
      }
  ]
  ads = ad_group_ad_service.mutate(operations)

  # Display results.
  for ad in ads['value']:
    print ('Ad with ID \'%s\' and of type \'%s\' was added.'
           % (ad['ad']['id'], ad['ad']['Ad.Type']))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, AD_GROUP_ID)
