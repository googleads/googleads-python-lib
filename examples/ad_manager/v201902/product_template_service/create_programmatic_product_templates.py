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

"""This example creates a programmatic product template.
"""

import uuid

# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  product_template_service = client.GetService(
      'ProductTemplateService', version='v201902')
  network_service = client.GetService(
      'NetworkService', version='v201902')

  product_template = {
      # Setting required Marketplace information.
      'productTemplateMarketplaceInfo': {
          'adExchangeEnvironment': 'DISPLAY'
      },
      # Setting common required fields for product templates.
      'name': ('Product template #%d' % uuid.uuid4()),
      'description': ('This product template creates standard programmatic'
                      'proposal line items targeting all ad units with'
                      'product segmentation on geo targeting.'),
      'nameMacro': ('<line-item-type> - <ad-unit> - '
                    '<template-name> - <location>'),
      'productType': 'DFP',
      'rateType': 'CPM',
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
      'lineItemType': 'STANDARD',
      'productSegmentation': {
          'geoSegment': {
              'targetedLocations': [
                  {'id': '2840',
                   'displayName': 'US'},
                  {'id': '2344',
                   'displayName': 'Hong Kong'}
              ]
          },
          'adUnitSegments': [{
              'adUnitId': (network_service.getCurrentNetwork()[
                  'effectiveRootAdUnitId']),
              'includeDescendants': 'true'
          }]
      }
  }

  product_templates = product_template_service.createProductTemplates(
      [product_template])

  if product_templates:
    for product_template in product_templates:
      print('A programmatic product template with ID "%s" and name "%s" '
            'was created.' % (product_template['id'],
                              product_template['name']))


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
