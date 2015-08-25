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

"""This code example gets all line item creative associations (LICA).

To create LICAs, run create_licas.py or associate_creative_set_to_line_item.py.
"""


# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  lica_service = client.GetService(
      'LineItemCreativeAssociationService', version='v201508')

  # Create a filter statement.
  statement = dfp.FilterStatement()

  # Get line items by statement.
  while True:
    response = lica_service.getLineItemCreativeAssociationsByStatement(
        statement.ToStatement())
    if 'results' in response:
      # Display results.
      for lica in response['results']:
        if 'creativeSetId' in lica:
          print ('LICA with line item ID \'%s\', creative set ID \'%s\', and '
                 'status \'%s\' was found.' %
                 (lica['lineItemId'], lica['creativeSetId'], lica['status']))
        else:
          print ('LICA with line item ID \'%s\', creative ID \'%s\', and status'
                 ' \'%s\' was found.' % (lica['lineItemId'], lica['creativeId'],
                                         lica['status']))

  print '\nNumber of results found: %s' % response['totalResultSetSize']

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
