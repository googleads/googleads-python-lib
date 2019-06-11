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

"""This example creates a ProductPartition tree.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import adwords

ADGROUP_ID = 'INSERT_AD_GROUP_ID_HERE'


class ProductPartitionHelper(object):
  """A helper for creating ProductPartition trees."""

  def __init__(self, adgroup_id):
    """Initializer.

    Args:
      adgroup_id: The ID of the AdGroup that we wish to attach the partition
                  tree to.
    """
    # The next temporary criterion ID to be used.
    # When creating our tree we need to specify the parent-child relationships
    # between nodes. However, until a criterion has been created on the server
    # we do not have a criterion ID with which to refer to it.
    # Instead we can specify temporary IDs that are specific to a single mutate
    # request. Once the criteria have been created they are assigned an ID as
    # normal and the temporary ID will no longer refer to it.
    # A valid temporary ID is any negative integer.
    self.next_id = -1
    # The set of mutate operations needed to create the current tree.
    self.operations = []
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


def main(client, adgroup_id):
  """Runs the example."""
  adgroup_criterion_service = client.GetService(
      'AdGroupCriterionService', version='v201809')

  helper = ProductPartitionHelper(adgroup_id)

  # The most trivial partition tree has only a unit node as the root, e.g.:
  # helper.CreateUnit(bid_amount=100000)

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

  helper.CreateUnit(root, new_product_canonical_condition, 200000)
  helper.CreateUnit(root, used_product_canonical_condition, 100000)
  other_condition = helper.CreateSubdivision(
      root, other_product_canonical_condition)

  cool_product_brand = {
      'xsi_type': 'ProductBrand',
      'value': 'CoolBrand'
  }

  cheap_product_brand = {
      'xsi_type': 'ProductBrand',
      'value': 'CheapBrand'
  }

  other_product_brand = {
      'xsi_type': 'ProductBrand',
  }

  helper.CreateUnit(other_condition, cool_product_brand, 900000)
  helper.CreateUnit(other_condition, cheap_product_brand, 10000)
  other_brand = helper.CreateSubdivision(other_condition, other_product_brand)

  # The value for the bidding category is a fixed ID for the 'Luggage & Bags'
  # category. You can retrieve IDs for categories from the ConstantDataService.
  # See the 'GetProductTaxonomy' example for more details.
  luggage_category = {
      'xsi_type': 'ProductBiddingCategory',
      'type': 'BIDDING_CATEGORY_L1',
      'value': '-5914235892932915235'
  }

  generic_category = {
      'xsi_type': 'ProductBiddingCategory',
      'type': 'BIDDING_CATEGORY_L1',
  }

  helper.CreateUnit(other_brand, luggage_category, 750000)
  helper.CreateUnit(other_brand, generic_category, 110000)

  # Make the mutate request
  result = adgroup_criterion_service.mutate(helper.GetOperations())

  children = {}

  root_node = None

  # For each criterion, make an array containing each of its children.
  # We always create the parent before the child, so we can rely on that here.
  for adgroup_criterion in result['value']:
    children[adgroup_criterion['criterion']['id']] = []

    if 'parentCriterionId' in adgroup_criterion['criterion']:
      children[adgroup_criterion['criterion']['parentCriterionId']].append(
          adgroup_criterion['criterion'])
    else:
      root_node = adgroup_criterion['criterion']

  # Show the tree
  DisplayTree(root_node, children)


def DisplayTree(node, children, level=0):
  """Recursively display a node and each of its children.

  Args:
    node: The node we're displaying the children of.
    children: Children of the parent node.
    level: How deep in the tree we are.
  """
  value = ''
  node_type = ''

  if 'caseValue' in node:
    case_value = node['caseValue']
    node_type = case_value['ProductDimension.Type']

    if node_type == 'ProductCanonicalCondition':
      value = (case_value['condition'] if 'condition' in case_value
               else 'OTHER')
    elif node_type == 'ProductBiddingCategory':
      value = '%s(%s)' % (case_value['type'], case_value['value']
                          if 'value' in case_value else 'OTHER')
    else:
      value = (case_value['value'] if 'value' in case_value else 'OTHER')

  print('%sid: %s, node_type: %s, value: %s\n'
        % (' ' * level, node['id'], node_type, value))

  for child_node in children[node['id']]:
    DisplayTree(child_node, children, level + 1)


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, ADGROUP_ID)
