#!/usr/bin/env python
#
# Copyright 2018 Google Inc. All Rights Reserved.
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

"""This code example adds a Gmail ad to a given ad group.

The ad group's campaign needs to have an AdvertisingChannelType of DISPLAY and
AdvertisingChannelSubType of DISPLAY_GMAIL_AD.

To get your ad groups, run get_ad_groups.py.
"""


# Import appropriate classes from the client library.
from googleads import adwords


ADGROUP_ID = 'INSERT_AD_GROUP_ID_HERE'


def main(client, ad_group_id):
  media_service = client.GetService('MediaService', 'v201809')
  ad_group_ad_service = client.GetService('AdGroupAdService', 'v201809')
  opener = client.proxy_config.BuildOpener()

  try:
    # This ad format doesn't allow the creation of an image using the Image.data
    # field. An image must first be created using the MediaService, and an
    # Image.mediaId must be populated when creating the ad.
    uploaded_logo_image = _CreateImage(
        media_service, opener, 'https://goo.gl/mtt54n')
    uploaded_marketing_image = _CreateImage(
        media_service, opener, 'http://goo.gl/3b9Wfh')

    teaser = {
        'headline': 'Dream',
        'description': 'Create your own adventure',
        'businessName': 'Interplanetary Ships',
        'logoImage': uploaded_logo_image
    }

    # Creates a Gmail ad.
    gmail_ad = {
        'xsi_type': 'GmailAd',
        'teaser': teaser,
        'marketingImage': uploaded_marketing_image,
        'marketingImageHeadline': 'Travel',
        'marketingImageDescription': 'Take to the skies!',
        'finalUrls': ['http://wwww.example.com']
    }

    # Creates ad group ad for the Gmail ad.
    ad_group_ad = {
        'adGroupId': ad_group_id,
        'ad': gmail_ad,
        # Optional: Set additional settings.
        'status': 'PAUSED'
    }

    # Creates ad group ad operations.
    operations = [{
        'operator': 'ADD',
        'operand': ad_group_ad
    }]

    # Adds a Gmail ad.
    ad_group_ads = ad_group_ad_service.mutate(operations)

    # Display results.
    for ad_group_ad in ad_group_ads['value']:
      print ('A Gmail ad with id "%d" and short headline "%s" was '
             'added.' % (ad_group_ad['ad']['id'],
                         ad_group_ad['ad']['teaser']['headline']))
  except Exception as e:
    raise Exception('Failed to create Gmail ad: %s' % e)


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


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()
  main(adwords_client, ADGROUP_ID)
