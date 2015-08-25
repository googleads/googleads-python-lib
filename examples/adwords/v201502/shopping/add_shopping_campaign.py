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

"""This example adds a Shopping campaign.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


import uuid

# Import appropriate modules from the client library.
from googleads import adwords

BUDGET_ID = 'INSERT_BUDGET_ID_HERE'
MERCHANT_ID = 'INSERT_MERCHANT_ID_HERE'


def main(client, budget_id, merchant_id):
  campaign_service = client.GetService('CampaignService', version='v201502')
  ad_group_service = client.GetService('AdGroupService', version='v201502')
  ad_group_ad_service = client.GetService('AdGroupAdService', version='v201502')

  # Create campaign
  campaign = {
      'name': 'Shopping campaign #%s' % uuid.uuid4(),
      # The advertisingChannelType is what makes this a shopping campaign
      'advertisingChannelType': 'SHOPPING',
      # Set shared budget (required)
      'budget': {
          'budgetId': budget_id
      },
      'biddingStrategyConfiguration': {
          'biddingStrategyType': 'MANUAL_CPC'
      },
      'settings': [
          # All shopping campaigns need a ShoppingSetting
          {
              'xsi_type': 'ShoppingSetting',
              'salesCountry': 'US',
              'campaignPriority': '0',
              'merchantId': merchant_id,
              # Set to "True" to enable Local Inventory Ads in your campaign.
              'enableLocal': True
          }
      ]
  }

  campaign_operations = [{
      'operator': 'ADD',
      'operand': campaign
  }]

  result = campaign_service.mutate(campaign_operations)

  for campaign in result['value']:
    print ('Campaign with name \'%s\' and ID \'%s\' was added.'
           % (campaign['name'], campaign['id']))

  # Create the AdGroup
  adgroup = {
      'campaignId': campaign['id'],
      'name': 'AdGroup #%s' % uuid.uuid4()
  }

  adgroup_operations = {
      'operator': 'ADD',
      'operand': adgroup
  }

  # Make the mutate request to add the AdGroup to the Shopping Campaign
  ad_group_result = ad_group_service.mutate(adgroup_operations)

  for adgroup in ad_group_result['value']:
    print ('AdGroup with name \'%s\' and ID \'%s\' was added.'
           % (adgroup['name'], adgroup['id']))

  # Create an AdGroup Ad
  adgroup_ad = {
      'adGroupId': adgroup['id'],
      # Create ProductAd
      'ad': {
          'xsi_type': 'ProductAd',
          'Ad.Type': 'ProductAd'
      }
  }

  ad_operation = {
      'operator': 'ADD',
      'operand': adgroup_ad
  }

  # Make the mutate request to add the ProductAd to the AdGroup
  ad_result = ad_group_ad_service.mutate([ad_operation])

  for adgroup_ad in ad_result['value']:
    print 'ProductAd with ID \'%s\' was added.' % adgroup_ad['ad']['id']


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, BUDGET_ID, MERCHANT_ID)
