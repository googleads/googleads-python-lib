#!/usr/bin/env python
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

"""This example creates a product package item.

To determine which product package items exist, run
get_all_product_package_items.py
"""

# Import appropriate modules from the client library.
from googleads import ad_manager

# Set the ID of the product package to add product package items to.
PRODUCT_PACKAGE_ID = 'INSERT_PRODUCT_PACKAGE_ID_HERE'

# Set the ID of the product to generate a product package item from.
PRODUCT_ID = 'INSERT_PRODUCT_ID_HERE'


def main(client):
  product_package_item_service = client.GetService('ProductPackageItemService',
                                                   version='v201905')

  product_package_item = {
      # Set the product from which the product package item is created.
      'productId': PRODUCT_ID,
      # Set the product package that the product package item belongs to.
      'productPackageId': PRODUCT_PACKAGE_ID,
      # Specify if the product package item is required for this
      # product package.
      'isMandatory': True
  }

  # Create the product package item on the server.
  result = product_package_item_service.createProductPackageItems(
      [product_package_item])

  for new_product_package_item in result:
    print ('A product package with ID %d created from product ID %d '
           'belonging to product package with ID %d was created.' %
           (new_product_package_item['id'],
            new_product_package_item['productId'],
            new_product_package_item['productPackageId']))


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
