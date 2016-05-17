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

"""This code example gets all line item creative associations (LICA) for a given
line item id.

To create LICAs, run create_licas.py."""


# Import appropriate modules from the client library.
from googleads import dfp

# Set the id of the line item to get LICAs by.
LINE_ITEM_ID = 'INSERT_LINE_ITEM_ID_HERE'


def main(client, line_item_id):
  # Initialize appropriate service.
  lica_service = client.GetService(
      'LineItemCreativeAssociationService', version='v201605')

# Create statement object to only select LICAs for the given line item id.
  values = [{
      'key': 'lineItemId',
      'value': {
          'xsi_type': 'NumberValue',
          'value': line_item_id
      }
  }]
  query = 'WHERE lineItemId = :lineItemId'
  statement = dfp.FilterStatement(query, values)

  while True:
    # Get LICAs by statement.
    response = lica_service.getLineItemCreativeAssociationsByStatement(
        statement.ToStatement())

    if 'results' in response:
      # Display results.
      for lica in response['results']:
        print ('LICA with line item id \'%s\', creative id \'%s\', and status '
               '\'%s\' was found.' % (lica['lineItemId'], lica['creativeId'],
                                      lica['status']))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

    print '\nNumber of results found: %s' % response['totalResultSetSize']

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, LINE_ITEM_ID)
