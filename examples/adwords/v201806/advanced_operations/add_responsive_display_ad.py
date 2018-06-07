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

import urllib2

from googleads import adwords


AD_GROUP_ID = 'INSERT_AD_GROUP_ID_HERE'


def main(client, ad_group_id):
  # Initialize appropriate services.
  ad_group_ad_service = client.GetService('AdGroupAdService', version='v201806')
  media_service = client.GetService('MediaService', version='v201806')
  opener = urllib2.build_opener(*client.proxy_config.GetHandlers())

  try:
    # Create marketing image.
    marketing_image = _CreateImage(media_service, opener,
                                   'https://goo.gl/3b9Wfh')

    # Create square marketing image.
    square_marketing_image = _CreateImage(media_service, opener,
                                          'https://goo.gl/mtt54n')

    # Create a responsive display ad.
    operations = [{
        'operator': 'ADD',
        'operand': {
            'xsi_type': 'AdGroupAd',
            'adGroupId': ad_group_id,
            'ad': {
                'xsi_type': 'ResponsiveDisplayAd',
                'marketingImage': {'mediaId': marketing_image['mediaId']},
                'shortHeadline': 'Travel',
                'longHeadline': 'Travel the World',
                'description': 'Take to the air!',
                'businessName': 'Interplanetary Cruises',
                'finalUrls': ['http://www.example.com'],
                # Optional: Set a square marketing image to the ad.
                'squareMarketingImage': {
                    'mediaId': square_marketing_image['mediaId']
                },
                # Optional: Set call-to-action text.
                'callToActionText': 'Shop Now',
                # Optional: Set dynamic display ad settings, composed of
                # landscape logo image, promotion text, and price prefix.
                'dynamicDisplayAdSettings': _CreateDynamicDisplayAdSettings(
                    media_service, opener),
                # Whitelisted accounts only: Set color settings using
                # hexadecimal numbers.
                # Set allowFlexibleColor to False if you want your ads to render
                # by always using your colors strictly.
                # 'mainColor': '#0000ff',
                # 'accentColor': '#ffff00',
                # 'allowFlexibleColor': False
                # Whitelisted accounts only: Set the format setting that the ad
                # will be served in.
                # 'formatSetting': 'NON_NATIVE'

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


def _CreateImage(media_service, opener, url):
  """Creates an image and uploads it to the server.

  Args:
    media_service: a SudsServiceProxy instance for AdWords's MediaService.
    opener: an OpenerDirector instance.
    url: a str URL used to load image data.

  Returns:
    The image that was successfully uploaded.
  """
  # Note: The utf-8 decode is for 2to3 Python 3 compatibility.
  image_data = opener.open(url).read().decode('utf-8')
  image = {
      'type': 'IMAGE',
      'data': image_data,
      'xsi_type': 'Image'
  }

  return media_service.upload(image)[0]


def _CreateDynamicDisplayAdSettings(media_service, opener):
  """Creates settings for dynamic display ad.

  Args:
    media_service: a SudsServiceProxy instance for AdWords's MediaService.
    opener: an OpenerDirector instance.

  Returns:
    The dynamic display ad settings.
  """
  image = _CreateImage(media_service, opener, 'https://goo.gl/dEvQeF')

  logo = {
      'type': 'IMAGE',
      'mediaId': image['mediaId'],
      'xsi_type': 'Image'
  }

  dynamic_settings = {
      'landscapeLogoImage': logo,
      'pricePrefix': 'as low as',
      'promoText': 'Free shipping!',
      'xsi_type': 'DynamicSettings',
  }

  return dynamic_settings


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, AD_GROUP_ID)
