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
"""This example gets all product package items.
"""

# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  # Initialize appropriate service.
  product_package_item_service = client.GetService(
      'ProductPackageItemService', version='v201805')

  # Create a statement to select product package items.
  statement = ad_manager.StatementBuilder()

  # Retrieve a small amount of product package items at a time, paging
  # through until all product package items have been retrieved.
  while True:
    response = product_package_item_service.getProductPackageItemsByStatement(
        statement.ToStatement())
    if 'results' in response and len(response['results']):
      for product_package_item in response['results']:
        # Print out some information for each product package item.
        print('Product package item with ID "%d", product id "%d", and product '
              'package id "%d" was found.\n' %
              (product_package_item['id'], product_package_item['productId'],
               product_package_item['productPackageId']))
      statement.offset += statement.limit
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
