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
"""This example gets all line items that are missing creatives.
"""

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  line_item_service = client.GetService('LineItemService', version='v201705')
  query = 'WHERE isMissingCreatives = :isMissingCreatives'
  values = [
      {'key': 'isMissingCreatives',
       'value': {
           'xsi_type': 'BooleanValue',
           'value': 'true'
       }},
  ]
  # Create a statement to select line items.
  statement = dfp.FilterStatement(query, values)

  # Retrieve a small amount of line items at a time, paging
  # through until all line items have been retrieved.
  while True:
    response = line_item_service.getLineItemsByStatement(statement.ToStatement(
    ))
    if 'results' in response:
      for line_item in response['results']:
        # Print out some information for each line item.
        print('Line item with ID "%d" and name "%s" was found.\n' %
              (line_item['id'], line_item['name']))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
