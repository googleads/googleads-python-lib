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

"""This code example creates a new programmatic proposal line item.
"""


import datetime
import uuid

# Import appropriate modules from the client library.
from googleads import ad_manager
import pytz

# Set the ID of the programmatic proposal that the proposal line item will
# belong to.
PROPOSAL_ID = 'INSERT_PROPOSAL_ID_HERE'

# Set the ID of the product that the proposal line items should be created from.
PRODUCT_ID = 'INSERT_PRODUCT_ID_HERE'

# Set the ID of the Marketplace rate card the proposal line items should be
# priced from.
RATE_CARD_ID = 'INSERT_RATE_CARD_ID_HERE'


def main(client, proposal_id, product_id, rate_card_id):
  # Initialize appropriate service.
  proposal_line_item_service = client.GetService(
      'ProposalLineItemService', version='v201811')
  network_service = client.GetService('NetworkService', version='v201811')

  # Get the root ad unit to target.
  root_ad_unit_id = (
      network_service.getCurrentNetwork()['effectiveRootAdUnitId'])

  start_datetime = datetime.datetime.now(tz=pytz.timezone('America/New_York'))
  end_datetime = start_datetime + datetime.timedelta(days=365)

  # Create a single programmatic proposal line item.
  proposal_line_item = {
      # Setting required Marketplace information.
      'marketplaceInfo': {
          'adExchangeEnvironment': 'DISPLAY'
      },
      # Setting common required fields for proposal line items.
      'name': 'Proposal line item #%s' % uuid.uuid4(),
      'rateCardId': rate_card_id,
      'productId': product_id,
      'proposalId': proposal_id,
      'targeting': {
          'inventoryTargeting': {
              'targetedAdUnits': {
                  'adUnitId': root_ad_unit_id
              }
          }
      },
      'startDateTime': start_datetime,
      'endDateTime': end_datetime,
      'goal': {
          'units': '1000',
          'unitType': 'IMPRESSIONS',
      },
      'netCost': {
          'currencyCode': 'USD',
          'microAmount': '2000000'
      },
      'netRate': {
          'currencyCode': 'USD',
          'microAmount': '2000000'
      },
      'rateType': 'CPM',
  }

  # Add programmatic proposal line items.
  proposal_line_items = proposal_line_item_service.createProposalLineItems(
      [proposal_line_item])

  # Display results.
  for proposal_line_item in proposal_line_items:
    print ('Programmatic proposal line item with id "%s", belonging to '
           'proposal id "%s", and named "%s" was created.' %
           (proposal_line_item['id'], proposal_line_item['proposalId'],
            proposal_line_item['name']))


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, PROPOSAL_ID, PRODUCT_ID, RATE_CARD_ID)

