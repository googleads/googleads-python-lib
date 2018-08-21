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

"""This code example requests buyer acceptance for a single proposal.
"""


# Import appropriate modules from the client library.
from googleads import ad_manager

PROPOSAL_ID = 'INSERT_PROPOSAL_ID_HERE'


def main(client, proposal_id):
  # Initialize appropriate service.
  proposal_service = client.GetService('ProposalService', version='v201805')

  # Create query.
  statement = (ad_manager.StatementBuilder()
               .Where('id = :proposalId')
               .WithBindVariable('proposalId', proposal_id))
  proposals_pushed_to_marketplace = 0

  # Get proposals by statement.
  while True:
    response = proposal_service.getProposalsByStatement(statement.ToStatement())
    if 'results' in response and len(response['results']):
      # Display results.
      for proposal in response['results']:
        print ('Programmatic proposal with id "%s", name "%s", and status '
               '"%s" will be pushed to Marketplace.' % (proposal['id'],
                                                        proposal['name'],
                                                        proposal['status']))
      # Perform action.
      result = proposal_service.performProposalAction(
          {'xsi_type': 'RequestBuyerAcceptance'}, statement.ToStatement())
      if result and int(result['numChanges']) > 0:
        proposals_pushed_to_marketplace += int(result['numChanges'])
      statement.offset += statement.limit
    else:
      break

  # Display results.
  if proposals_pushed_to_marketplace > 0:
    print ('\nNumber of programmatic proposals pushed to Marketplace: %s'
           % proposals_pushed_to_marketplace)
  else:
    print '\nNo programmatic proposals were pushed to Marketplace.'


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, PROPOSAL_ID)
