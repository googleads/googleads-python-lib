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

"""This example creates a programmatic product for non-sales management.
"""

import uuid

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  product_service = client.GetService('ProductService', version='v201708')
  network_service = client.GetService('NetworkService', version='v201708')

  product = {
      # Setting required Marketplace Information.
      'productMarketplaceInfo': {
          'additionalTerms': 'Remember to also discuss that thing.',
          'adExchangeEnvironment': 'DISPLAY'
      },

      # Setting common required fields for products.
      'name': ('Product #%d' % uuid.uuid4()),
      'productType': 'DFP',
      'rateType': 'CPM',
      'lineItemType': 'STANDARD',
      'priority': 8,
      'environment': 'BROWSER',
      'rate': {
          'currencyCode': 'USD',
          'microAmount': '6000000'
      },
      'creativePlaceholders': [
          {
              'size': {
                  'width': '728',
                  'height': '90'
              }
          },
          {
              'size': {
                  'width': '300',
                  'height': '250'
              }
          }
      ],
      'builtInTargeting': {
          'inventoryTargeting': {
              'adUnitTargeting': {
                  'adUnitId': network_service.getCurrentNetwork()[
                      'effectiveRootAdUnitId'],
                  'includeDescendents': 'true'
              }
          }
      },
  }

  products = product_service.createProducts([product])

  if products:
    for product in products:
      print ('A programmatic product for non-sales management with ID "%s"'
             ' and name "%s" was created.' % (product['id'], product['name']))


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
