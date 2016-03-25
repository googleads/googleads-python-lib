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

"""This example adds a text add that uses advanced features of upgraded URLS.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

from googleads import adwords
from googleads import errors


ADGROUP_ID = 'INSERT_ADGROUP_ID_HERE'


def main(client, adgroup_id):
  # Initialize appropriate service.
  adgroup_ad_service = client.GetService('AdGroupAdService', version='v201603')

  # Create the text ad
  text_ad = {
      'xsi_type': 'TextAd',
      'headline': 'Luxury Cruise to Mars',
      'description1': 'Visit the Red Planet in style.',
      'description2': 'Low-gravity fun for everyone!',
      'displayUrl': 'www.example.com',
      # Specify a tracking URL for 3rd party tracking provider. You may specify
      # one at customer, campaign, ad group, ad, criterion or feed item levels.
      'trackingUrlTemplate': ('http://tracker.example.com/?season={_season}'
                              '&promocode={_promocode}&u={lpurl}'),
      'urlCustomParameters': {
          'parameters': [
              # Since your tracking URL has two custom parameters, provide
              # their values too. This can be provided at campaign, ad group,
              # ad, criterion, or feed item levels.
              {
                  'key': 'season',
                  'value': 'christmas'
              },
              {
                  'key': 'promocode',
                  'value': 'NYC123'
              }
          ]
      },
      # Specify a list of final URLs. This field cannot be set if URL
      # field is set, or finalUrls is unset. This may be specified at ad,
      # criterion, and feed item levels.
      'finalUrls': [
          'http://www.example.com/cruise/space/',
          'http://www.example.com/locations/mars/'
      ],
      # Specify a list of final mobile URLs. This field cannot be set if URL
      # field is set, or finalUrls is unset. This may be specified at ad,
      # criterion, and feed item levels.
      'finalMobileUrls': [
          'http://mobile.example.com/cruise/space/',
          'http://mobile.example.com/locations/mars/'
      ]
  }

  text_adgroup_ad = {
      'adGroupId': adgroup_id,
      'ad': text_ad,
      # Optional: Set the status.
      'status': 'PAUSED'
  }

  operations = [{
      'operator': 'ADD',
      'operand': text_adgroup_ad
  }]

  response = adgroup_ad_service.mutate(operations)

  if 'value' in response:
    for adgroup_ad in response['value']:
      print ('AdGroupAd with ID %s and display URL \'%s\'was added.'
             % (adgroup_ad['ad']['id'], adgroup_ad['ad']['displayUrl']))
      print 'Upgraded URL properties:'
      print 'Final Urls: %s' % adgroup_ad['ad']['finalUrls']
      print 'Final Mobile URLs: %s' % adgroup_ad['ad']['finalMobileUrls']
      print ('Tracking URL template: %s'
             % adgroup_ad['ad']['trackingUrlTemplate'])
      print 'Custom parameters: %s' % adgroup_ad['ad']['urlCustomParameters']
  else:
    raise errors.GoogleAdsError('Failed to create AdGroupAd.')


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, ADGROUP_ID)
