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

"""This code example archives a proposal line item.

To determine which proposal line items exist, run
get_all_proposal_line_items.py.
"""


# Import appropriate modules from the client library.
from googleads import ad_manager

# Set the id of the proposal line item to archive.
PROPOSAL_LINE_ITEM_ID = 'INSERT_PROPOSAL_LINE_ITEM_ID_HERE'


def main(client, proposal_line_item_id):
  # Initialize appropriate service.
  proposal_line_item_service = client.GetService(
      'ProposalLineItemService', version='v202005')

  # Create query.
  statement = (ad_manager.StatementBuilder(version='v202005')
               .Where('id = :id')
               .WithBindVariable('id', int(proposal_line_item_id))
               .Limit(1))

  proposal_line_items_archived = 0

  # Get proposal line items by statement.
  while True:
    response = proposal_line_item_service.getProposalLineItemsByStatement(
        statement.ToStatement())
    if 'results' in response and len(response['results']):
      for proposal_line_item in response['results']:
        print('Proposal line item with id "%s", '
              'belonging to proposal id "%s", and '
              'name "%s" will be archived.' %
              (proposal_line_item['id'], proposal_line_item['proposalId'],
               proposal_line_item['name']))

      # Perform action.
      result = proposal_line_item_service.performProposalLineItemAction(
          {'xsi_type': 'ArchiveProposalLineItems'}, statement.ToStatement())
      if result and int(result['numChanges']) > 0:
        proposal_line_items_archived += int(result['numChanges'])
      statement.offset += statement.limit
    else:
      break

  # Display results.
  if proposal_line_items_archived > 0:
    print('Number of proposal line items '
          'archived: %s' % proposal_line_items_archived)
  else:
    print('No proposal line items were archived.')


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, PROPOSAL_LINE_ITEM_ID)
