#!/usr/bin/env python
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

"""This example updates a product template's GeoTargeting.

To determine which product templates exist, run get_all_product_templates.py.

"""


# Import appropriate modules from the client library.
from googleads import dfp

PRODUCT_TEMPLATE_ID = 'INSERT_PRODUCT_TEMPLATE_ID_HERE'


def main(client, product_template_id):
  # Initialize appropriate service.
  product_template_service = client.GetService(
      'ProductTemplateService', version='v201702')

  # Create a statement to select a single product template by ID.
  values = [{
      'key': 'id',
      'value': {
          'xsi_type': 'NumberValue',
          'value': product_template_id
      }
  }]
  query = 'WHERE id = :id ORDER BY id ASC'
  statement = dfp.FilterStatement(query, values, 1)

  # Get product templates by statement.
  response = product_template_service.getProductTemplatesByStatement(
      statement.ToStatement())

  if 'results' in response:
    # Update each local product template object by appending a new geo-target.
    for product_template in response['results']:
      # Create geo-targeting for Canada to append.
      location = {
          'id': '2124',
          'displayName': 'Canada'
      }

      try:
        targeting = product_template['builtInTargeting']

        if 'geoTargeting' in targeting:
          geo_targeting = targeting['geoTargeting']

          if 'targetedLocations' in geo_targeting:
            geo_targeting['targetedLocations'].append(location)
          else:
            geo_targeting['targetedLocations'] = [location]
        else:
          targeting['geoTargeting'] = {
              'targetedLocations': [location]
          }
      except KeyError:
        product_template['builtInTargeting'] = {
            'geoTargeting': {
                'targetedLocations': [location]
            }
        }

      # Update products remotely.
      product_templates = product_template_service.updateProductTemplates(
          [product_template])

    # Display results.
    if product_templates:
      for product_template in product_templates:
        print ('Product template with id \'%s\' and name \'%s\' was '
               'updated.' % (product_template['id'], product_template['name']))
    else:
      print 'No product templates were updated.'
  else:
    print 'No product templates found to update.'


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, PRODUCT_TEMPLATE_ID)
