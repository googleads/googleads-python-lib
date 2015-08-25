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

"""This code example creates a new run-of-network proposal line item.

To determine which proposal line items exist, run
get_all_proposal_line_items.py. To determine which proposals exist, run
get_all_proposals.py.
"""


from datetime import date
import uuid

# Import appropriate modules from the client library.
from googleads import dfp

# Set proposal that the created proposal line item will belong to.
PROPOSAL_ID = 'INSERT_PROPOSAL_ID_HERE'

# Set the ID of the product that the proposal line items should be created from.
PRODUCT_ID = 'INSERT_PRODUCT_ID_HERE'

# Set the ID of the rate card the proposal line items should be priced from.
RATE_CARD_ID = 'INSERT_RATE_CARD_ID_HERE'


def main(client, proposal_id, product_id, rate_card_id):
  # Initialize appropriate service.
  proposal_line_item_service = client.GetService(
      'ProposalLineItemService', version='v201505')
  network_service = client.GetService('NetworkService', version='v201505')

  # Get the root ad unit to target.
  root_ad_unit_id = (
      network_service.getCurrentNetwork()['effectiveRootAdUnitId'])

  # Create a single proposal line item.
  proposal_line_item = {
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
      'startDateTime': {
          'date': {
              'year': str(date.today().year),
              'month': str(date.today().month),
              'day': str(date.today().day)
          },
          'hour': '23',
          'minute': '59',
          'second': '59'
      },
      'endDateTime': {
          'date': {
              'year': str(date.today().year + 1),
              'month': '9',
              'day': '30'
          },
          'hour': '0',
          'minute': '0',
          'second': '0',
          'timeZoneID': 'America/Los_Angeles'
      },
      'deliveryRateType': 'EVENLY',
      'creativeRotationType': 'OPTIMIZED',
      'billingCap': 'CAPPED_CUMULATIVE',
      'billingSource': 'THIRD_PARTY_VOLUME',
      'goal': {
          'units': '1000',
          'unitType': 'IMPRESSIONS',
      },
      'cost': {
          'currencyCode': 'USD',
          'microAmount': '2000000'
      },
      'costPerUnit': {
          'currencyCode': 'USD',
          'microAmount': '2000000'
      },
      'rateType': 'CPM',
  }

  # Add proposal line items.
  proposal_line_items = proposal_line_item_service.createProposalLineItems(
      [proposal_line_item])

  # Display results.
  for proposal_line_item in proposal_line_items:
    print ('Proposal line item with id \'%s\', belonging to proposal id \'%s\''
           ', and named \'%s\' was created.' %
           (proposal_line_item['id'], proposal_line_item['proposalId'],
            proposal_line_item['name']))


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, PROPOSAL_ID, PRODUCT_ID, RATE_CARD_ID)

