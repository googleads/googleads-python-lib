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

"""This example upgrades an ad to use upgraded URLs.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

from googleads import adwords
from googleads import errors


ADGROUP_ID = 'INSERT_ADGROUP_ID_HERE'
AD_ID = 'INSERT_AD_ID_HERE'


def main(client, adgroup_id, ad_id):
  # Initialize appropriate service.
  adgroup_ad_service = client.GetService('AdGroupAdService', version='v201603')

  selector = {
      'fields': ['Id', 'Url'],
      'predicates': [
          {
              'field': 'AdGroupId',
              'operator': 'EQUALS',
              'values': [adgroup_id]
          },
          {
              'field': 'Id',
              'operator': 'EQUALS',
              'values': [ad_id]
          }
      ]
  }

  page = adgroup_ad_service.get(selector)

  adgroup_ad = page['entries'][0] if page['entries'] else None

  if not adgroup_ad:
    raise errors.GoogleAdsError('Ad not found.')

  ad_url_upgrade = {
      'adId': adgroup_ad['ad']['id'],
      'finalUrl': adgroup_ad['ad']['url']
  }

  adgroup_ad = adgroup_ad_service.upgradeUrl([ad_url_upgrade])[0]

  if adgroup_ad:
    print ('AdGroupAd with ID %s and destination URL \'%s\' was upgraded.'
           % (adgroup_ad['id'], adgroup_ad['finalUrls'][0]))
  else:
    raise errors.GoogleAdsError('Failed to create AdGroupAd.')


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, ADGROUP_ID, AD_ID)
