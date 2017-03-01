#!/usr/bin/python
#
# Copyright 2017 Google Inc. All Rights Reserved.
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

"""This example adds a Shopping campaign for Showcase ads.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.
"""

import base64
import uuid

from googleads import adwords
from suds import WebFault


BUDGET_ID = 'INSERT_BUDGET_ID_HERE'
MERCHANT_ID = 'INSERT_MERCHANT_ID_HERE'
EXPANDED_IMAGE_FILEPATH = 'INSERT_PATH_TO_EXPANDED_IMAGE'
COLLAPSED_IMAGE_FILEPATH = 'INSERT_PATH_TO_COLLAPSED_IMAGE'


class ProductPartitionHelper(object):
  """A helper for creating ProductPartition trees."""

  # The next temporary criterion ID to be used.
  # When creating our tree we need to specify the parent-child relationships
  # between nodes. However, until a criterion has been created on the server we
  # do not have a criterion ID with which to refer to it.
  # Instead we can specify temporary IDs that are specific to a single mutate
  # request. Once the criteria have been created they are assigned an ID as
  # normal and the temporary ID will no longer refer to it.
  # A valid temporary ID is any negative integer.
  next_id = -1

  # The set of mutate operations needed to create the current tree.
  operations = []

  def __init__(self, adgroup_id):
    """Initializer.

    Args:
      adgroup_id: The ID of the AdGroup that we wish to attach the partition
                  tree to.
    """
    self.adgroup_id = adgroup_id

  def CreateSubdivision(self, parent=None, value=None):
    """Creates a subdivision node.

    Args:
      parent: The node that should be this node's parent.
      value: The value being partitioned on.
    Returns:
      A new subdivision node.
    """
    division = {
        'xsi_type': 'ProductPartition',
        'partitionType': 'SUBDIVISION',
        'id': str(self.next_id)
    }

    # The root has neither a parent nor a value.
    if parent is not None:
      division['parentCriterionId'] = parent['id']
      division['caseValue'] = value

    adgroup_criterion = {
        'xsi_type': 'BiddableAdGroupCriterion',
        'adGroupId': self.adgroup_id,
        'criterion': division
    }

    self.CreateAddOperation(adgroup_criterion)
    self.next_id -= 1

    return division

  def CreateUnit(self, parent=None, value=None, bid_amount=None):
    """Creates a unit node.

    Args:
      parent: The node that should be this node's parent.
      value: The value being partitioned on.
      bid_amount: The amount to bid for matching products, in micros.
    Returns:
      A new unit node.
    """
    unit = {
        'xsi_type': 'ProductPartition',
        'partitionType': 'UNIT'
    }

    # The root node has neither a parent nor a value.
    if parent is not None:
      unit['parentCriterionId'] = parent['id']
      unit['caseValue'] = value

    if bid_amount is not None and bid_amount > 0:
      bidding_strategy_configuration = {
          'bids': [{
              'xsi_type': 'CpcBid',
              'bid': {
                  'xsi_type': 'Money',
                  'microAmount': str(bid_amount)
              }
          }]
      }

      adgroup_criterion = {
          'xsi_type': 'BiddableAdGroupCriterion',
          'biddingStrategyConfiguration': bidding_strategy_configuration
      }
    else:
      adgroup_criterion = {
          'xsi_type': 'NegativeAdGroupCriterion'
      }

    adgroup_criterion['adGroupId'] = self.adgroup_id
    adgroup_criterion['criterion'] = unit

    self.CreateAddOperation(adgroup_criterion)

    return unit

  def GetOperations(self):
    """Returns the set of mutate operations needed to create the current tree.

    Returns:
      The set of operations
    """
    return self.operations

  def CreateAddOperation(self, criterion):
    """Creates an AdGroupCriterionOperation for the given criterion.

    Args:
      criterion: The criterion we want to add.
    """
    operation = {
        'operator': 'ADD',
        'operand': criterion
    }

    self.operations.append(operation)


def main(client, budget_id, merchant_id, expanded_image_filepath,
         collapsed_image_filepath):
  try:
    # Create the Shopping Campaign
    campaign = CreateShoppingCampaign(client, budget_id, merchant_id)

    # Create the AdGroup
    adgroup = CreateAdGroup(client, campaign['id'])

    # Create a Showcase Ad
    CreateShowcaseAd(client, adgroup, expanded_image_filepath,
                     collapsed_image_filepath)

    product_partition_tree = CreateProductPartition(client, adgroup['id'])
    print 'Final tree:\n%s' % product_partition_tree
  except WebFault:
    print 'Failed to create shopping campaign for showcase ads.'
    raise


def CreateShoppingCampaign(client, budget_id, merchant_id):
  """Creates a shopping campaign with the given budget and merchant IDs.

  Args:
    client: an AdWordsClient instance.
    budget_id: the str ID of the budget to be associated with the shopping
      campaign.
    merchant_id: the str ID of the merchant account to be associated with the
      shopping campaign.

  Returns:
    The created Shopping Campaign as a sudsobject.
  """
  campaign_service = client.GetService('CampaignService', 'v201702')

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

  campaign = campaign_service.mutate(campaign_operations)['value'][0]
  print ('Campaign with name \'%s\' and ID \'%s\' was added.'
         % (campaign['name'], campaign['id']))

  return campaign


def CreateAdGroup(client, campaign_id):
  """Creates an AdGroup for the given shopping campaign ID.

  Args:
    client: an AdWordsClient instance.
    campaign_id: the str ID of a shopping campaign.

  Returns:
    The created AdGroup as a sudsobject.
  """
  ad_group_service = client.GetService('AdGroupService', 'v201702')

  adgroup = {
      # Required: Set the ad group type to SHOPPING_SHOWCASE_ADS
      'adGroupType': 'SHOPPING_SHOWCASE_ADS',
      'campaignId': campaign_id,
      'name': 'AdGroup #%s' % uuid.uuid4(),
      # REQUIRED: Set the ad group's bidding strategy configuration.
      'biddingStrategyConfiguration': {
          # Showcase ads require either ManualCpc or EnhancedCpc.
          'biddingStrategyType': 'MANUAL_CPC',
          # Optional: Set the bids
          'bids': [{
              'xsi_type': 'CpcBid',
              'bid': {
                  'microAmount': 100000
              }
          }]
      }
  }

  adgroup_operations = {
      'operator': 'ADD',
      'operand': adgroup
  }

  # Make the mutate request to add the AdGroup to the Shopping Campaign
  adgroup = ad_group_service.mutate(adgroup_operations)['value'][0]

  print ('AdGroup with name "%s" and ID "%s" was added.'
         % (adgroup['name'], adgroup['id']))

  return adgroup


def CreateShowcaseAd(client, adgroup, expanded_image_filepath,
                     collapsed_image_filepath):
  """Creates a showcase add for the given AdGroup with the given images.

  Args:
    client: an AdWordsClient instance.
    adgroup: a dict or suds object defining an AdGroup for a Shopping Campaign.
    expanded_image_filepath: a str filepath to a .jpg file that will be used as
      the Showcase Ad's expandedImage.
    collapsed_image_filepath: a str filepath to a .jpg file that will be used as
      the Showcase Ad's collapsedImage.

  Returns:
    The created Showcase Ad as a sudsobject.
  """
  ad_group_ad_service = client.GetService('AdGroupAdService', 'v201702')

  showcase_ad = {
      'adGroupId': adgroup['id'],
      'ad': {
          'xsi_type': 'ShowcaseAd',
          'Ad.Type': 'ShowcaseAd',
          # Required: set the ad's name, final URLs, and display URL.
          'name': 'Showcase ad #%s' % uuid.uuid4(),
          'finalUrls': 'http://example.com/showcase',
          'displayUrl': 'example.com',
          # Required: Set the ad's expanded image.
          'expandedImage': {
              'mediaId': UploadImage(client, expanded_image_filepath)['mediaId']
          },
          # Optional: Set the collapsed image.
          'collapsedImage': {
              'mediaId':
                  UploadImage(client, collapsed_image_filepath)['mediaId']
          }
      }
  }

  ad_operation = {
      'operator': 'ADD',
      'operand': showcase_ad
  }

  # Make the mutate request to add the ProductAd to the AdGroup
  showcase_ad = ad_group_ad_service.mutate([ad_operation])['value'][0]

  print 'ShowcaseAd with ID "%s" was added.' % showcase_ad['ad']['id']

  return showcase_ad


def UploadImage(client, filepath):
  """Uploads a .jpg image with the given filepath via the AdWords MediaService.

  Args:
    client: an AdWordsClient instance.
    filepath: a str filepath to the .jpg file to be uploaded.

  Returns:
    The created Image as a sudsobject.
  """
  media_service = client.GetService('MediaService', 'v201702')

  with open(filepath, 'rb') as image_handle:
    image_data = base64.encodestring(image_handle.read()).decode('utf-8')

  image = [{
      'xsi_type': 'Image',
      'data': image_data,
      'type': 'IMAGE'
  }]

  image = media_service.upload(image)[0]

  return image


def CreateProductPartition(client, adgroup_id):
  """Creates a ProductPartition tree for the given AdGroup ID.

  Args:
    client: an AdWordsClient instance.
    adgroup_id: a str AdGroup ID.

  Returns:
    The ProductPartition tree as a sudsobject.
  """
  ad_group_criterion_service = client.GetService('AdGroupCriterionService',
                                                 'v201702')
  helper = ProductPartitionHelper(adgroup_id)
  root = helper.CreateSubdivision()

  new_product_canonical_condition = {
      'xsi_type': 'ProductCanonicalCondition',
      'condition': 'NEW'
  }

  used_product_canonical_condition = {
      'xsi_type': 'ProductCanonicalCondition',
      'condition': 'USED'
  }

  other_product_canonical_condition = {
      'xsi_type': 'ProductCanonicalCondition',
  }

  helper.CreateUnit(root, new_product_canonical_condition)
  helper.CreateUnit(root, used_product_canonical_condition)
  helper.CreateUnit(root, other_product_canonical_condition)

  result = ad_group_criterion_service.mutate(helper.operations)
  return result['value']


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, BUDGET_ID, MERCHANT_ID, EXPANDED_IMAGE_FILEPATH,
       COLLAPSED_IMAGE_FILEPATH)
