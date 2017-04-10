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

"""This code example updates the destination URL of all line item creative
associations (LICA).

To determine which LICAs exist, run get_all_licas.py.
"""


# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  lica_service = client.GetService(
      'LineItemCreativeAssociationService', version='v201611')

  # Create statement object to get all LICAs.
  statement = dfp.FilterStatement()

  while True:
    # Get LICAs by statement.
    response = lica_service.getLineItemCreativeAssociationsByStatement(
        statement.ToStatement())

    if 'results' in response:
      # Update each local LICA object by changing its destination URL.
      updated_licas = []
      for lica in response['results']:
        lica['destinationUrl'] = 'http://news.google.com'
        updated_licas.append(lica)

      # Update LICAs remotely.
      licas = lica_service.updateLineItemCreativeAssociations(updated_licas)

      # Display results.
      for lica in licas:
        print ('LICA with line item id \'%s\', creative id \'%s\', and status '
               '\'%s\' was updated.' % (lica['lineItemId'], lica['creativeId'],
                                        lica['status']))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  if response['totalResultSetSize'] == 0:
    print 'No LICAs found to update.'

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
