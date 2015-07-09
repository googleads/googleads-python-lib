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

"""This example fetches the set of valid ProductBiddingCategories.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: ConstantDataService.getProductBiddingCategoryData
"""

__author__ = ('api.msaniscalchi@gmail.com (Mark Saniscalchi)',
              'Joseph DiLallo')

# Import appropriate modules from the client library.
from googleads import adwords


def main(client):
  service = client.GetService('ConstantDataService', version='v201506')

  selector = {
      'predicates': [
          {
              'field': 'Country',
              'operator': 'IN',
              'values': ['US']
          }
      ]
  }

  result = service.getProductBiddingCategoryData(selector)

  bidding_categories = {}
  root_categories = []

  for product_bidding_category in result:
    category_id = product_bidding_category['dimensionValue']['value']
    parent_id = None
    name = product_bidding_category['displayValue'][0]['value']

    # Note: There may be cases where there isn't a value.
    if ('parentDimensionValue' in product_bidding_category and
        'value' in product_bidding_category['parentDimensionValue']):
      parent_id = product_bidding_category['parentDimensionValue']['value']

    if category_id not in bidding_categories:
      bidding_categories[category_id] = {}

    category = bidding_categories[category_id]

    if parent_id is not None:
      if parent_id not in bidding_categories:
        bidding_categories[parent_id] = {}

      parent = bidding_categories[parent_id]

      if 'children' not in parent:
        parent['children'] = []

      parent['children'].append(category)
    else:
      root_categories.append(category)

    category['id'] = category_id
    category['name'] = name

  DisplayCategories(root_categories)


def DisplayCategories(categories, prefix=''):
  for category in categories:
    print '%s%s [%s]' % (prefix, category['name'], category['id'])

    if 'children' in category:
      DisplayCategories(category['children'], '%s%s > ' % (prefix,
                                                           category['name']))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client)
