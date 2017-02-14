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

"""This code example publishes a product to Marketplace.
"""


# Import appropriate modules from the client library.
from googleads import dfp

# Set the id of the product to publish.
PRODUCT_ID = 'INSERT_PRODUCT_ID_HERE'


def main(client, product_id):
  # Initialize appropriate service.
  product_service = client.GetService('ProductService', version='v201702')

  # Create query.
  values = [{
      'key': 'id',
      'value': {
          'xsi_type': 'NumberValue',
          'value': product_id
      }
  }]
  query = 'WHERE id = :id'
  statement = dfp.FilterStatement(query, values, 1)

  products_published = 0

  # Get products by statement.
  while True:
    response = product_service.getProductsByStatement(
        statement.ToStatement())
    if 'results' in response:
      for product in response['results']:
        print ('Product with id \'%s\' and name \'%s\' will be '
               'published.' % (product['id'],
                               product['name']))

      # Perform action.
      result = product_service.performProductAction(
          {'xsi_type': 'PublishProducts'}, statement.ToStatement())
      if result and int(result['numChanges']) > 0:
        products_published += int(result['numChanges'])
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  # Display results.
  if products_published > 0:
    print 'Number of programmatic products published: %s' % products_published
  else:
    print 'No products were published.'


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, PRODUCT_ID)
