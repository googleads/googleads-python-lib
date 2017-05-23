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

"""This example creates a product package.

To determine which product packages exist, run get_all_product_packages.py
"""

# Import appropriate modules from the client library.
import random

from googleads import dfp

# Set the ID of the rate card to associate with the product package.
RATE_CARD_ID = 'INSERT_RATE_CARD_ID_HERE'


def main(client):
  product_package_service = client.GetService('ProductPackageService',
                                              version='v201702')

  # Create a local product package.
  product_package = {
      'name': 'Product Package #%d' % random.randint(0, 100000000),
      'rateCardIds': [RATE_CARD_ID]
  }

  result = product_package_service.createProductPackages([product_package])

  for new_product_package in result:
    print ('A product package with ID %d and name \'%s\' was created.' %
           (new_product_package['id'], new_product_package['name']))


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
