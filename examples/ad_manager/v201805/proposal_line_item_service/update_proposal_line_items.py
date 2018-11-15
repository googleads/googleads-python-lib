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

"""This code example updates a proposal line item's notes.

To determine which proposal line items exist,
run get_all_proposal_line_items.py.
"""


# Import appropriate modules from the client library.
from googleads import ad_manager

# Set id of the proposal line item to update.
PROPOSAL_LINE_ITEM_ID = 'INSERT_PROPOSAL_LINE_ITEM_ID_HERE'


def main(client, proposal_line_item_id):
  # Initialize appropriate service.
  proposal_line_item_service = client.GetService(
      'ProposalLineItemService', version='v201805')

  # Create statement to select a proposal line item.

  statement = (ad_manager.StatementBuilder(version='v201805')
               .Where('id = :id')
               .WithBindVariable('id', long(proposal_line_item_id))
               .Limit(1))

  # Get proposal line items by statement.
  response = proposal_line_item_service.getProposalLineItemsByStatement(
      statement.ToStatement())

  if 'results' in response and len(response['results']):
    # Update each the proposal line item's notes field.
    proposal_line_item = response['results'][0]
    proposal_line_item['internalNotes'] = 'Proposal line is ready to submit.'

    # Update proposal line items remotely.
    proposal_line_items = proposal_line_item_service.updateProposalLineItems(
        [proposal_line_item])

    # Display results.
    if proposal_line_items:
      for proposal_line_item in proposal_line_items:
        print ('Line item with id "%s", belonging to proposal id "%s" and,'
               ' named "%s" was updated.' % (
                   proposal_line_item['id'], proposal_line_item['proposalId'],
                   proposal_line_item['name']))
    else:
      print 'No proposal line items were updated.'
  else:
    print 'No proposal line items found to update.'


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, PROPOSAL_LINE_ITEM_ID)
