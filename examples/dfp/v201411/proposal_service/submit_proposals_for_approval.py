#!/usr/bin/python
#
# Copyright 2014 Google Inc. All Rights Reserved.
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

"""This code example approves a single proposal.

To determine which proposals exist, run get_all_proposals.py."""


# Import appropriate modules from the client library.
from googleads import dfp

PROPOSAL_ID = 'INSERT_PROPOSAL_ID_HERE'

def main(client, proposal_id):
  # Initialize appropriate service.
  proposal_service = client.GetService('ProposalService', version='v201411')

  # Create query.
  values = [{
      'key': 'proposalId',
      'value': {
          'xsi_type': 'TextValue',
          'value': proposal_id
      }
  }]
  query = 'WHERE id = :proposalId'

  # Create a filter statement.
  statement = dfp.FilterStatement(query, values)
  proposals_approved = 0

  # Get proposals by statement.
  while True:
    response = proposal_service.getProposalsByStatement(statement.ToStatement())
    if 'results' in response:
      # Display results.
      for proposal in response['results']:
        print ('Proposal with id \'%s\', name \'%s\', and status \'%s\' will be'
               ' approved.' % (proposal['id'], proposal['name'],
                               proposal['status']))
      # Perform action.
      result = proposal_service.performProposalAction(
          {'xsi_type': 'SubmitProposalsForApproval'}, statement.ToStatement())
      if result and int(result['numChanges']) > 0:
        proposals_approved += int(result['numChanges'])
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  # Display results.
  if proposals_approved > 0:
    print '\nNumber of proposals approved: %s' % proposals_approved
  else:
    print '\nNo proposals were approved.'

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, PROPOSAL_ID)
