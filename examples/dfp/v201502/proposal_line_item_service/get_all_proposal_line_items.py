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

"""This code example gets all proposal line items.

To create proposal line items, run create_proposal_line_items.py.
"""


# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  proposal_line_item_service = client.GetService(
      'ProposalLineItemService', version='v201502')

  # Create a filter statement.
  statement = dfp.FilterStatement('ORDER BY id ASC')

  # Get proposal line items by statement.
  while True:
    response = proposal_line_item_service.getProposalLineItemsByStatement(
        statement.ToStatement())
    if 'results' in response:
      # Display results.
      for idx, proposal_line_item in enumerate(response['results'],
                                               start=statement.offset):
        print ('%s) Proposal line item with id \'%s\', belonging to proposal id'
               ' \'%s\', and named \'%s\' was found.' %
               (idx, proposal_line_item['id'], proposal_line_item['proposalId'],
                proposal_line_item['name']))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
