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

"""This code example gets all proposals that are currently 'PENDING_APPROVAL.'

To create proposals, run create_proposals.py."""


# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  proposal_service = client.GetService('ProposalService', version='v201502')

  # Create statement object to select a single proposal by an ID.
  values = [{
      'key': 'status',
      'value': {
          'xsi_type': 'TextValue',
          'value': 'PENDING_APPROVAL'
      }
  }]
  query = 'WHERE status = :status ORDER BY id ASC'

  statement = dfp.FilterStatement(query, values)

  # Get proposals by statement.
  while True:
    response = proposal_service.getProposalsByStatement(statement.ToStatement())
    if 'results' in response:
      # Display results.
      for proposal in response['results']:
        print ('Proposal with id \'%s\' name \'%s\' was found.'
               % (proposal['id'], proposal['name']))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
