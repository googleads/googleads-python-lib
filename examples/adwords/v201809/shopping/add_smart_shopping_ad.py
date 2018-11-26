#!/usr/bin/env python
#
# Copyright 2018 Google LLC
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

"""This example adds a Smart Shopping campaign with an ad group and ad group ad.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.
"""


import uuid

# Import appropriate modules from the client library.
from googleads import adwords

# If set to true, a default partition will be created.
# Set it to false if you plan to run the add_product_partition_tree.py
# example right after this example.
CREATE_DEFAULT_PARTITION = False
MERCHANT_ID = 'INSERT_MERCHANT_ID_HERE'


def main(client, merchant_id, create_default_partition):
  budget_id = CreateBudget(client)
  campaign_id = CreateSmartCampaign(client, budget_id, merchant_id)
  ad_group_id = CreateSmartShoppingAdGroup(client, campaign_id)
  CreateSmartShoppingAd(client, ad_group_id)

  if create_default_partition:
    CreateDefaultPartition(client, ad_group_id)


def CreateBudget(client):
  """Adds a new budget.

  Args:
    client: an AdWordsClient instance.
  Returns:
    A budget ID.
  """
  budget_service = client.GetService('BudgetService', version='v201809')

  budget = {
      'name': 'Interplanetary budget #%s' % uuid.uuid4(),
      'amount': {
          'microAmount': '50000000'
      },
      'deliveryMethod': 'STANDARD',
      # Non-shared budgets are required for Smart Shopping campaigns.
      'isExplicitlyShared': False
  }

  budget_operations = [{
      'operator': 'ADD',
      'operand': budget
  }]

  # Add the budget.
  budget_id = budget_service.mutate(budget_operations)['value'][0][
      'budgetId']

  return budget_id


def CreateSmartCampaign(client, budget_id, merchant_id):
  """Adds a new Smart Shopping campaign.

  Args:
    client: an AdWordsClient instance.
    budget_id: the str ID of the budget to be associated with the Shopping
      campaign.
    merchant_id: the str ID of the merchant account to be associated with the
      Shopping campaign.
  Returns:
    A campaign ID.
  """
  campaign_service = client.GetService('CampaignService', version='v201809')
  # Create campaign with required and optional settings.
  campaign = {
      'name': 'Shopping campaign #%s' % uuid.uuid4(),
      # The advertisingChannelType is what makes this a Shopping campaign.
      'advertisingChannelType': 'SHOPPING',
      # Sets the advertisingChannelSubType to SHOPPING_GOAL_OPTIMIZED_ADS to
      # make this a Smart Shopping campaign.
      'advertisingChannelSubType': 'SHOPPING_GOAL_OPTIMIZED_ADS',
      # Recommendation: Set the campaign to PAUSED when creating it to stop the
      # ads from immediately serving. Set to ENABLED once you've added targeting
      # and the ads are ready to serve.
      'status': 'PAUSED',
      # Set portfolio budget (required).
      'budget': {'budgetId': budget_id},
      # Set a bidding strategy. Only MAXIMIZE_CONVERSION_VALUE is supported.
      'biddingStrategyConfiguration': {
          'biddingStrategyType': 'MAXIMIZE_CONVERSION_VALUE'
      },
      'settings': [{
          # All Shopping campaigns need a ShoppingSetting.
          'xsi_type': 'ShoppingSetting',
          'salesCountry': 'US',
          'merchantId': merchant_id
      }]
  }

  campaign_operations = [{
      'operator': 'ADD',
      'operand': campaign
  }]

  result = campaign_service.mutate(campaign_operations)['value'][0]

  print ('Smart Shopping campaign with name "%s" and ID "%s" was added.'
         % (result['name'], result['id']))

  return result['id']


def CreateSmartShoppingAdGroup(client, campaign_id):
  """Adds a new Smart Shopping ad group.

  Args:
    client: an AdWordsClient instance.
    campaign_id: the str ID of a Smart Shopping campaign.
  Returns:
    An ad group ID.
  """
  ad_group_service = client.GetService('AdGroupService', version='v201809')
  # Create the ad group.
  ad_group = {
      'campaignId': campaign_id,
      'name': 'Smart Shopping ad group #%s' % uuid.uuid4(),
      # Set the ad group type to SHOPPING_GOAL_OPTIMIZED_ADS.
      'adGroupType': 'SHOPPING_GOAL_OPTIMIZED_ADS'
  }

  adgroup_operations = {
      'operator': 'ADD',
      'operand': ad_group
  }

  # Make the mutate request to add the AdGroup to the Smart Shopping campaign.
  ad_group = ad_group_service.mutate(adgroup_operations)['value'][0]
  ad_group_id = ad_group['id']

  print ('AdGroup with name "%s" and ID "%s" was added.'
         % (ad_group['name'], ad_group_id))

  return ad_group_id


def CreateSmartShoppingAd(client, ad_group_id):
  """Adds a new Smart Shopping ad.

  Args:
    client: an AdWordsClient instance.
    ad_group_id: an integer ID for an ad group.
  """
  ad_group_ad_service = client.GetService('AdGroupAdService', version='v201809')
  # Create an AdGroup Ad.
  adgroup_ad = {
      'adGroupId': ad_group_id,
      # Create a Smart Shopping ad (Goal-optimized Shopping ad).
      'ad': {
          'xsi_type': 'GoalOptimizedShoppingAd'
      }
  }

  ad_operation = {
      'operator': 'ADD',
      'operand': adgroup_ad
  }

  # Make the mutate request to add the Smart Shopping ad to the AdGroup.
  ad_result = ad_group_ad_service.mutate([ad_operation])

  for adgroup_ad in ad_result['value']:
    print 'Smart Shopping ad with ID "%s" was added.' % adgroup_ad['ad']['id']


def CreateDefaultPartition(client, ad_group_id):
  """Creates a default partition.

  Args:
    client: an AdWordsClient instance.
    ad_group_id: an integer ID for an ad group.
  """
  ad_group_criterion_service = client.GetService('AdGroupCriterionService',
                                                 version='v201809')

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

  main(adwords_client, MERCHANT_ID, CREATE_DEFAULT_PARTITION)
