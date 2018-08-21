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

"""This example creates a product package item base rate.

To determine which base rates exist, run get_all_base_rates.py
"""

# Import appropriate modules from the client library.
from googleads import ad_manager

# Set the rate card ID to add the base rate to.
RATE_CARD_ID = 'INSERT_RATE_CARD_ID_HERE'

# Set the product package item to apply this base rate to.
PRODUCT_PACKAGE_ITEM_ID = 'INSERT_PRODUCT_PACKAGE_ID_HERE'


def main(client):
  # Initialize appropriate service.
  base_rate_service = client.GetService('BaseRateService', version='v201805')

  # Create a base rate for a product package item.
  product_package_item_base_rate = {
      'xsi_type': 'ProductPackageItemBaseRate',
      # Set the rate card ID that the product package item base rate
      # belongs to.
      'rateCardId': RATE_CARD_ID,
      # Set the product package item the base rate will be applied to.
      'productPackageItemId': PRODUCT_PACKAGE_ITEM_ID,
      # Create a rate worth $2 USD and set that on the product package item
      # base rate.
      'rate': {
          'xsi_type': 'Money',
          'currencyCode': 'USD',
          'microAmount': 2000000,
      }
  }

  # Create the product package item base rate on the server.
  result = base_rate_service.createBaseRates([product_package_item_base_rate])

  for new_base_rate in result:
    print ('A product package item base rate with ID %d and rate %f %s '
           'was created.' % (new_base_rate['id'],
                             new_base_rate['microAmount'],
                             new_base_rate['currencyCode']))


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
