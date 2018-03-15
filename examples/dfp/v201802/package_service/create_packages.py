#!/usr/bin/env python
#
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This example creates a package.

To determine which packages exist, run get_all_packages.py.
"""

# Import appropriate modules from the client library.
import random

from googleads import dfp

# Set the ID of the product package to create the package from.
PRODUCT_PACKAGE_ID = 'INSERT_PRODUCT_PACKAGE_ID_HERE'

# Set the ID of the proposal to create proposal line items under.
PROPOSAL_ID = 'INSERT_PROPOSAL_ID_HERE'

# Set the ID of the rate card the proposal line items belonging to the product
# package are priced from.
RATE_CARD_ID = 'INSERT_RATE_CARD_ID_HERE'


def main(client):
  # Initialize appropriate service.
  package_service = client.GetService('PackageService', version='v201802')

  # Create local package.
  package = {
      'name': 'Package #%d' % random.randint(0, 1000000),
      'proposalId': PROPOSAL_ID,
      'productPackageId': PRODUCT_PACKAGE_ID,
      'rateCardId': RATE_CARD_ID,
  }

  # Create the package on the server.
  result = package_service.createPackages([package])

  for new_package in result:
    print ('A package with ID %d and name "%s" was created' %
           (new_package['id'], new_package['name']))


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
