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
"""This example gets all line item creative associations.
"""

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  lica_service = client.GetService(
      'LineItemCreativeAssociationService', version='v201608')

  # Create a statement to select line item creative associations.
  statement = dfp.FilterStatement()

  # Retrieve a small amount of line item creative associations at a time, paging
  # through until all line item creative associations have been retrieved.
  while True:
    response = lica_service.getLineItemCreativeAssociationsByStatement(
        statement.ToStatement())
    if 'results' in response:
      for lica in response['results']:
        # Print out some information for each line item creative association.
        if 'creativeSetId' in lica:
          print('LICA with line item ID \'%s\', creative set ID \'%s\', and '
                'status \'%s\' was found.' %
                (lica['lineItemId'], lica['creativeSetId'], lica['status']))
        else:
          print('Line item creative association with line item ID "%d" and '
                'creative ID "%d" was found.\n' %
                (lica['lineItemId'], lica['creativeId']))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
