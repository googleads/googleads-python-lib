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

"""This example gets all products created from a product template.

"""


# Import appropriate modules from the client library.
from googleads import dfp

PRODUCT_TEMPLATE_ID = 'INSERT_PRODUCT_TEMPLATE_ID_HERE'


def main(client, product_template_id):
  # Initialize appropriate service.
  product_service = client.GetService('ProductService', version='v201511')

  # Create a filter statement to select only products created from a single
  # a product template.
  values = [{
      'key': 'productTemplateId',
      'value': {
          'xsi_type': 'NumberValue',
          'value': product_template_id
      }
  }]
  query = 'WHERE productTemplateId = :productTemplateId ORDER BY id ASC'
  statement = dfp.FilterStatement(query, values)

  # Get products by statement.
  while True:
    response = product_service.getProductsByStatement(statement.ToStatement())
    if 'results' in response:
      # Display results.
      for product in response['results']:
        print ('Product with id \'%s\' and name \'%s\' was found.' % (
            product['id'], product['name']))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, PRODUCT_TEMPLATE_ID)
