#!/usr/bin/env python
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

"""This example adds a responsive display ad to a given ad group.

To get ad_group_id, run get_ad_groups.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

import base64
import urllib2

from googleads import adwords


AD_GROUP_ID = 'INSERT_AD_GROUP_ID_HERE'


def main(client, ad_group_id):
  # Initialize appropriate services.
  ad_group_ad_service = client.GetService('AdGroupAdService', version='v201705')
  media_service = client.GetService('MediaService', version='v201705')

  try:
    # Create image.
    opener = urllib2.build_opener(*client.proxy_config.GetHandlers())
    image_data = base64.b64encode(opener.open('https://goo.gl/3b9Wfh').read())
    image = {
        'type': 'IMAGE',
        'data': image_data,
        'xsi_type': 'Image'
    }

    # Make the upload request
    image = media_service.upload(image)[0]

    # Create a responsive display ad.
    operations = [{
        'operator': 'ADD',
        'operand': {
            'xsi_type': 'AdGroupAd',
            'adGroupId': ad_group_id,
            'ad': {
                'xsi_type': 'ResponsiveDisplayAd',
                'marketingImage': {'mediaId': image['mediaId']},
                'shortHeadline': 'Travel',
                'longHeadline': 'Travel the World',
                'description': 'Take to the air!',
                'businessName': 'Interplanetary Cruises',
                'finalUrls': ['http://www.example.com']
            },
            # Optional fields.
            'status': 'PAUSED'
        }
    }]

    # Make the mutate request.
    ads = ad_group_ad_service.mutate(operations)

    # Display results.
    for ad in ads['value']:
      print ('ResponsiveDisplayAd with id "%d" and short headline "%s" was '
             'added.' % (ad['ad']['id'], ad['ad']['shortHeadline']))

  except:
    raise Exception('Failed to create responsive display ad.')


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, AD_GROUP_ID)
