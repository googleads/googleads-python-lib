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

"""This example updates an expanded text ad.

To get expanded text ads, run get_expanded_text_ads.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

import uuid
from googleads import adwords


AD_ID = 'INSERT_AD_ID_HERE'


def main(client, ad_id):
  # Initialize appropriate service.
  ad_service = client.GetService('AdService', version='v201809')

  # Create an expanded text ad using the provided ad ID.
  expanded_text_ad = {
      'xsi_type': 'ExpandedTextAd',
      'id': ad_id,
      'headlinePart1': 'Cruise to Pluto #' + str(uuid.uuid4())[:8],
      'headlinePart2': 'Tickets on sale now',
      'description': 'Best space cruise ever.',
      'finalUrls': ['http://www.example.com'],
      'finalMobileUrls': ['http://www.example.com/mobile']
  }

  # Create ad group ad operation.
  operations = [{
      'operator': 'SET',
      'operand': expanded_text_ad
  }]

  # Updates the ad on ther server.
  result = ad_service.mutate(operations)
  updated_ad = result['value'][0]

  print 'Expanded text ad with ID %s was updated.' % updated_ad['id']
  print ('\tHeadline part 1: %s\nHeadline part 2: %s\nDescription: %s\n'
         'Final URL: %s\nFinal mobile URL: %s' %
         (updated_ad['headlinePart1'],
          updated_ad['headlinePart2'],
          updated_ad['description'],
          updated_ad['finalUrls'][0],
          updated_ad['finalMobileUrls'][0]))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, AD_ID)
