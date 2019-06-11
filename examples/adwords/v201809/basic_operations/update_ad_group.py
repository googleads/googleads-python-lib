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

"""This example updates the CPC bid and status for a given ad group.

To get ad groups, run get_ad_groups.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

from googleads import adwords


AD_GROUP_ID = 'INSERT_AD_GROUP_ID_HERE'
CPC_BID_MICRO_AMOUNT = 'INSERT_CPC_BID_MICRO_AMOUNT_HERE'


def main(client, ad_group_id, bid_micro_amount=None):
  # Initialize appropriate service.
  ad_group_service = client.GetService('AdGroupService', version='v201809')

  # Construct operations and update an ad group.
  operations = [{
      'operator': 'SET',
      'operand': {
          'id': ad_group_id,
          'status': 'PAUSED'
      }
  }]

  if bid_micro_amount:
    operations[0]['operand']['biddingStrategyConfiguration'] = {
        'bids': [{
            'xsi_type': 'CpcBid',
            'bid': {
                'microAmount': bid_micro_amount,
            }
        }]
    }

  ad_groups = ad_group_service.mutate(operations)

  # Display results.
  for ad_group in ad_groups['value']:
    bidding_strategy_configuration = ad_group['biddingStrategyConfiguration']
    # Find the CpcBid in the bidding strategy configuration's bids collection.
    cpc_bid_micros = None

    if bidding_strategy_configuration:
      bids = bidding_strategy_configuration['bids']

      if bids:
        for bid in bids:
          if bid['Bids.Type'] == 'CpcBid':
            cpc_bid_micros = bid['bid']['microAmount']
            break

    print('Ad group with name "%s", and id "%s" was updated to have status '
          '"%s" and CPC bid %d.'
          % (ad_group['name'], ad_group['id'], ad_group['status'],
              cpc_bid_micros))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, AD_GROUP_ID, CPC_BID_MICRO_AMOUNT)
