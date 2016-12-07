#!/usr/bin/python
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
"""This example gets all product templates.
"""

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  product_template_service = client.GetService(
      'ProductTemplateService', version='v201611')

  # Create a statement to select product templates.
  statement = dfp.FilterStatement()

  # Retrieve a small amount of product templates at a time, paging
  # through until all product templates have been retrieved.
  while True:
    response = product_template_service.getProductTemplatesByStatement(
        statement.ToStatement())
    if 'results' in response:
      for product_template in response['results']:
        # Print out some information for each product template.
        print('Product template with ID "%d" and name "%s" was found.\n' %
              (product_template['id'], product_template['name']))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
