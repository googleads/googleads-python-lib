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
"""This example gets all products created from a product template.
"""

# Import appropriate modules from the client library.
from googleads import dfp

PRODUCT_TEMPLATE_ID = 'INSERT_PRODUCT_TEMPLATE_ID_HERE'


def main(client, product_template_id):
  # Initialize appropriate service.
  product_service = client.GetService('ProductService', version='v201802')

  # Create a statement to select products.
  statement = (dfp.StatementBuilder()
               .Where('productTemplateId = :productTemplateId')
               .WithBindVariable('productTemplateId', product_template_id))

  # Retrieve a small amount of products at a time, paging
  # through until all products have been retrieved.
  while True:
    response = product_service.getProductsByStatement(statement.ToStatement())
    if 'results' in response:
      for product in response['results']:
        # Print out some information for each product.
        print('Product with ID "%d" and name "%s" was found.\n' %
              (product['id'], product['name']))
      statement.offset += statement.limit
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, PRODUCT_TEMPLATE_ID)
