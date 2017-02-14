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

"""This example updates a product's notes.

To determine which products exist, run get_all_products.py.

"""


# Import appropriate modules from the client library.
from googleads import dfp

PRODUCT_ID = 'INSERT_PRODUCT_ID_HERE'


def main(client, product_id):
  # Initialize appropriate service.
  product_service = client.GetService('ProductService', version='v201702')

  # Create statement object to select a single product by an ID.
  values = [{
      'key': 'id',
      'value': {
          'xsi_type': 'NumberValue',
          'value': product_id
      }
  }]
  query = 'WHERE id = :id'
  statement = dfp.FilterStatement(query, values, 1)

  # Get products by statement.
  response = product_service.getProductsByStatement(statement.ToStatement())

  if 'results' in response:
    # Update each local product object by changing its notes.
    updated_products = []
    for product in response['results']:
      product['notes'] = 'Product needs further review before activation.'
      updated_products.append(product)

    # Update products remotely.
    products = product_service.updateProducts(updated_products)

    # Display results.
    if products:
      for product in products:
        print ('Product with id \'%s\', name \'%s\', and '
               'notes \'%s\' was updated.'
               % (product['id'], product['name'], product['notes']))
    else:
      print 'No products were updated.'
  else:
    print 'No products found to update.'

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, PRODUCT_ID)
