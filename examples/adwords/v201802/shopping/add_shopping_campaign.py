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
# If set to true, a default partition will be created. If running the
# add_product_partition_tree.py example right after this example, make
# sure this stays set to false.
CREATE_DEFAULT_PARTITION = False
MERCHANT_ID = 'INSERT_MERCHANT_ID_HERE'


def main(client, budget_id, merchant_id, create_default_partition):
  campaign_service = client.GetService('CampaignService', version='v201802')
  ad_group_service = client.GetService('AdGroupService', version='v201802')
  ad_group_ad_service = client.GetService('AdGroupAdService', version='v201802')

  # Create campaign
  campaign = {
      'name': 'Shopping campaign #%s' % uuid.uuid4(),
      # The advertisingChannelType is what makes this a shopping campaign
      'advertisingChannelType': 'SHOPPING',
      # Recommendation: Set the campaign to PAUSED when creating it to stop the
      # ads from immediately serving. Set to ENABLED once you've added targeting
      # and the ads are ready to serve.
      'status': 'PAUSED',
      # Set portfolio budget (required)
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
    print ('Campaign with name "%s" and ID "%s" was added.'
           % (campaign['name'], campaign['id']))

  # Create the AdGroup
  ad_group = {
      'campaignId': campaign['id'],
      'name': 'AdGroup #%s' % uuid.uuid4()
  }

  adgroup_operations = {
      'operator': 'ADD',
      'operand': ad_group
  }

  # Make the mutate request to add the AdGroup to the Shopping Campaign
  ad_group = ad_group_service.mutate(adgroup_operations)['value'][0]
  ad_group_id = ad_group['id']

  print ('AdGroup with name "%s" and ID "%s" was added.'
         % (ad_group['name'], ad_group_id))

  # Create an AdGroup Ad
  adgroup_ad = {
      'adGroupId': ad_group_id,
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
    print 'ProductAd with ID "%s" was added.' % adgroup_ad['ad']['id']

  if create_default_partition:
    CreateDefaultPartition(client, ad_group_id)


def CreateDefaultPartition(client, ad_group_id):
  """Creates a default partition.

  Args:
    client: an AdWordsClient instance.
    ad_group_id: an integer ID for an ad group.
  """
  ad_group_criterion_service = client.GetService('AdGroupCriterionService',
                                                 version='v201802')

  operations = [{
      'operator': 'ADD',
      'operand': {
          'xsi_type': 'BiddableAdGroupCriterion',
          'adGroupId': ad_group_id,
          # Make sure that caseValue and parentCriterionId are left unspecified.
          # This makes this partition as generic as possible to use as a
          # fallback when others don't match.
          'criterion': {
              'xsi_type': 'ProductPartition',
              'partitionType': 'UNIT'
          },
          'biddingStrategyConfiguration': {
              'bids': [{
                  'xsi_type': 'CpcBid',
                  'bid': {
                      'microAmount': 500000
                  }
              }]
          }
      }
  }]

  ad_group_criterion = ad_group_criterion_service.mutate(operations)['value'][0]

  print ('Ad group criterion with ID "%d" in ad group with ID "%d" was added.'
         % (ad_group_criterion['criterion']['id'],
            ad_group_criterion['adGroupId']))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, BUDGET_ID, MERCHANT_ID, CREATE_DEFAULT_PARTITION)
