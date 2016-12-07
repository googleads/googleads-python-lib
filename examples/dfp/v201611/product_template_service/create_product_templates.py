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

"""This example creates a product template.

To determine which product templates exist, run get_all_product_templates.py.
"""

import uuid

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  product_template_service = client.GetService(
      'ProductTemplateService', version='v201611')
  network_service = client.GetService(
      'NetworkService', version='v201611')

  # Create a product template.
  product_template = {
      'name': ('Product template #%d' % uuid.uuid4()),
      'description': ('This product template creates standard proposal line '
                      'items targeting Chrome browsers with product '
                      'segmentation on ad units and geo targeting.'),
      'nameMacro': ('<line-item-type> - <ad-unit> - '
                    '<template-name> - <location>'),
      'productType': 'DFP',
      'rateType': 'CPM',
      'roadblockingType': 'ONE_OR_MORE',
      'deliveryRateType': 'AS_FAST_AS_POSSIBLE',
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
      'customizableAttributes': {
          'allowPlacementTargetingCustomization': True,
      },
      'builtInTargeting': {
          'technologyTargeting': {
              # Set browser targeting to Chrome.
              'browserTargeting': {
                  {
                      'browsers': [
                          {
                              'id': '500072'
                          }
                      ]
                  }
              }
          }
      },
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

  # Create product templates on the server.
  product_templates = product_template_service.createProductTemplates(
      [product_template])

  if product_templates:
    for product_template in product_templates:
      print ('A product template with ID \'%s\' and name \'%s\' was '
             'created.' % (product_template['id'], product_template['name']))


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
