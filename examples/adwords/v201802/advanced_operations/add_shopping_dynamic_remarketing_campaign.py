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

"""Adds a Shopping dynamic remarketing campaign for the Display Network.

This example steps through the following:
* Creates a new Display Network campaign.
* Links the campaign with Merchant Center.
* Links the user list to the ad group.
* Creates a responsive display ad to render the dynamic text.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.
"""


import base64
import uuid

from googleads import adwords


MERCHANT_ID = 'INSERT_MERCHANT_CENTER_ID_HERE'
BUDGET_ID = 'INSERT_BUDGET_ID_HERE'
USER_LIST_ID = 'INSERT_USER_LIST_ID_HERE'


def main(client, merchant_id, budget_id, user_list_id):
  opener = client.proxy_config.BuildOpener()

  campaign = CreateCampaign(client, merchant_id, budget_id)
  campaign_id = campaign['id']
  print 'Campaign with name "%s" and ID "%d" was added.' % (
      campaign['name'], campaign_id)

  ad_group = CreateAdGroup(client, campaign_id)
  ad_group_id = ad_group['id']
  print 'Ad group with name "%s" and ID "%d" was added.' % (
      ad_group['name'], ad_group_id)

  ad_group_ad = CreateAd(client, opener, ad_group_id)
  print 'Responsive display ad with ID "%d" was added.' % (
      ad_group_ad['ad']['id'])

  AttachUserList(client, ad_group_id, user_list_id)
  print 'User list with ID "%d" was attached to ad group with ID "%d".' % (
      user_list_id, ad_group_id)


def CreateCampaign(client, merchant_id, budget_id):
  """Creates a new Display Network campaign.

  Args:
    client: an AdWordsClient instance.
    merchant_id: a int merchant center ID.
    budget_id: a int budget ID.

  Returns:
    The campaign that was successfully created.
  """
  campaign_service = client.GetService('CampaignService', 'v201802')

  campaign = {
      'name': 'Shopping campaign #%d' % uuid.uuid4(),
      # Dynamic remarketing campaigns are only available on the Google Display
      # Network.
      'advertisingChannelType': 'DISPLAY',
      'status': 'PAUSED',
      'budget': {
          'budgetId': budget_id
      },
      # This example uses a Manual CPC bidding strategy, but you should select
      # the strategy that best aligns with your sales goals. More details here:
      # https://support.google.com/adwords/answer/2472725
      'biddingStrategyConfiguration': {
          'biddingStrategyType': 'MANUAL_CPC'
      },
      'settings': [{
          'xsi_type': 'ShoppingSetting',
          # Campaigns with numerically higher priorities take precedence over
          # those with lower priorities.
          'campaignPriority': 0,
          'merchantId': merchant_id,
          # Display network campaigns do not support partition by country. The
          # only supported value is "ZZ". This signals that products from all
          # countries are available in this campaign. The actual products which
          # serve are based on the products tagged in the user list entry.
          'salesCountry': 'ZZ',
          # Optional: Enable local inventory ads (items for sale in physical
          # stores.)
          'enableLocal': True,
          # Optional: Declare whether purchases are only made on the merchant
          # store, or completed on Google.
          'purchasePlatform': 'MERCHANT'
      }]
  }

  operations = [{
      'operator': 'ADD',
      'operand': campaign
  }]

  return campaign_service.mutate(operations)['value'][0]


def CreateAdGroup(client, campaign_id):
  """Creates a dynamic remarketing campaign.

  Args:
    client: an AdWordsClient instance.
    campaign_id: an int campaign ID.

  Returns:
    The ad group that was successfully created.
  """
  ad_group_service = client.GetService('AdGroupService', 'v201802')

  ad_group = {
      'name': 'Dynamic remarketing ad group',
      'campaignId': campaign_id,
      'status': 'ENABLED'
  }

  operations = [{
      'operator': 'ADD',
      'operand': ad_group
  }]

  return ad_group_service.mutate(operations)['value'][0]


def CreateAd(client, opener, ad_group_id):
  """Creates a ResponsiveDisplayAd.

  Args:
    client: an AdWordsClient instance.
    opener: an OpenerDirector instance.
    ad_group_id: an int ad group ID.

  Returns:
    The ad group ad that was successfully created.
  """
  ad_group_ad_service = client.GetService('AdGroupAdService', 'v201802')
  media_service = client.GetService('MediaService', 'v201802')

  marketing_image_id = _CreateImage(
      media_service, opener, 'https://goo.gl/3b9Wfh')
  logo_image_id = _CreateImage(media_service, opener, 'https://goo.gl/mtt54n')

  ad = {
      'xsi_type': 'ResponsiveDisplayAd',
      # This ad format doesn't allow the creation of an image using the
      # Image.data field. An image must first be created using the MediaService,
      # and Image.mediaId must be populated when creating the ad.
      'marketingImage': {
          'xsi_type': 'Image',
          'mediaId': marketing_image_id
      },
      'shortHeadline': 'Travel',
      'longHeadline': 'Travel the World',
      'description': 'Take to the air!',
      'businessName': 'Interplanetary Cruises',
      'finalUrls': ['http://wwww.example.com'],
      # Optional: Call to action text.
      # Valid texts: https://support.google.com/adwords/answer/7005917
      'callToActionText': 'Apply Now',
      # Optional: Set dynamic display ad settings, composed of landscape logo
      # image, promotion text, and price prefix.
      'dynamicDisplayAdSettings': CreateDynamicDisplayAdSettings(
          client, opener),
      # Optional: Create a logo image and set it to the ad.
      'logoImage': {
          'xsi_type': 'Image',
          'mediaId': logo_image_id
      },
      # Optional: Create a square marketing image and set it to the ad.
      'squareMarketingImage': {
          'xsi_type': 'Image',
          'mediaId': logo_image_id
      },
      # Whitelisted accounts only: Set color settings using hexadecimal values.
      # Set allowFlexibleColor to False if you want your ads to render by always
      # using your colors strictly.
      # 'mainColor': '#000fff',
      # 'accentColor': '#fff000',
      # 'allowFlexibleColor': False,
      # Whitelisted accounts only: Set the format setting that the ad will be
      # served in.
      # 'formatSetting': 'NON_NATIVE'
  }

  ad_group_ad = {
      'ad': ad,
      'adGroupId': ad_group_id
  }

  operations = [{
      'operation': 'ADD',
      'operand': ad_group_ad
  }]

  return ad_group_ad_service.mutate(operations)['value'][0]


def AttachUserList(client, ad_group_id, user_list_id):
  """Links the provided ad group and user list.

  Args:
    client: an AdWordsClient instance.
    ad_group_id: an int ad group ID.
    user_list_id: an int user list ID.

  Returns:
    The ad group criterion that was successfully created.
  """
  ad_group_criterion_service = client.GetService(
      'AdGroupCriterionService', 'v201802')

  user_list = {
      'xsi_type': 'CriterionUserList',
      'userListId': user_list_id
  }

  ad_group_criterion = {
      'xsi_type': 'BiddableAdGroupCriterion',
      'criterion': user_list,
      'adGroupId': ad_group_id
  }

  operations = [{
      'operator': 'ADD',
      'operand': ad_group_criterion
  }]

  return ad_group_criterion_service.mutate(operations)['value'][0]


def CreateDynamicDisplayAdSettings(client, opener):
  """Creates dynamic display ad settings.

  Args:
    client: an AdWordsClient instance.
    opener: an OpenerDirector instance.

  Returns:
    A dict containing the dynamic display ad settings.
  """
  media_service = client.GetService('MediaService', 'v201802')

  logo = {
      'xsi_type': 'Image',
      'mediaId': _CreateImage(media_service, opener, 'https://goo.gl/dEvQeF')
  }

  dynamic_settings = {
      'landscapeLogoImage': logo,
      'pricePrefix': 'as low as',
      'promoText': 'Free shipping!'
  }

  return dynamic_settings


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
  image_data = base64.b64encode(opener.open(url).read()).decode('utf-8')
  image = {
      'type': 'IMAGE',
      'data': image_data,
      'xsi_type': 'Image'
  }

  return media_service.upload(image)[0]


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, MERCHANT_ID, BUDGET_ID, USER_LIST_ID)
