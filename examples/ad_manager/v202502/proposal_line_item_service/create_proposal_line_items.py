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

"""Creates a proposal line item."""


import datetime
import uuid

# Import appropriate modules from the client library.
from googleads import ad_manager
import pytz

# Set proposal that the created proposal line item will belong to.
PROPOSAL_ID = 'INSERT_PROPOSAL_ID_HERE'


def main(client, proposal_id):
  proposal_line_item_service = client.GetService(
      'ProposalLineItemService', version='v202502')
  network_service = client.GetService('NetworkService', version='v202502')

  start_datetime = datetime.datetime.now(tz=pytz.timezone('America/New_York'))
  end_datetime = start_datetime + datetime.timedelta(days=365)

  # Get the root ad unit to target.
  root_ad_unit_id = (
      network_service.getCurrentNetwork()['effectiveRootAdUnitId'])

  # Create a single programmatic proposal line item.
  proposal_line_item = {
      # Setting common required fields for proposal line items.
      'name': 'Proposal line item #%s' % uuid.uuid4(),
      'proposalId': proposal_id,
      'targeting': {
          'inventoryTargeting': {
              'targetedAdUnits': {
                  'adUnitId': root_ad_unit_id
              }
          },
          'requestPlatformTargeting': {
              'targetedRequestPlatforms': ['BROWSER']
          },
          # Target Display environment by excluding Mobile Apps.
          # DeviceCapabilities can be obtained though the Device_Capability PQL
          # table:
          # https://developers.google.com/ad-manager/api/reference/latest/PublisherQueryLanguageService
          'technologyTargeting': {
              'deviceCapabilityTargeting': [{'id': 5005}]
          }
      },
      'startDateTime': start_datetime,
      'endDateTime': end_datetime,
      'creativePlaceholders': [
          {
              'size': {
                  'width': '300',
                  'height': '250'
              }
          },
          {
              'size': {
                  'width': '120',
                  'height': '600'
              }
          }
      ],
      'goal': {
          'units': '1000',
          'unitType': 'IMPRESSIONS',
      },
      'netRate': {
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
    print('Proposal line item with id "%s", belonging to proposal with id "%s",'
          ' and named "%s" was created.' % (proposal_line_item['id'],
                                            proposal_line_item['proposalId'],
                                            proposal_line_item['name']))


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, PROPOSAL_ID)

