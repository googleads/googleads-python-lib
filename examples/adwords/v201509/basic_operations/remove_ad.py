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

"""This example deletes an ad using the 'REMOVE' operator.

To get ads, run get_text_ads.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


from googleads import adwords


AD_GROUP_ID = 'INSERT_AD_GROUP_ID_HERE'
AD_ID = 'INSERT_AD_ID_HERE'


def main(client, ad_group_id, ad_id):
  # Initialize appropriate service.
  ad_group_ad_service = client.GetService('AdGroupAdService', version='v201509')

  # Construct operations and delete ad.
  operations = [{
      'operator': 'REMOVE',
      'operand': {
          'xsi_type': 'AdGroupAd',
          'adGroupId': ad_group_id,
          'ad': {
              'id': ad_id
          }
      }
  }]
  result = ad_group_ad_service.mutate(operations)

  # Display results.
  for ad in result['value']:
    print ('Ad with id \'%s\' and type \'%s\' was deleted.'
           % (ad['ad']['id'], ad['ad']['Ad.Type']))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, AD_GROUP_ID, AD_ID)
