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

"""This example adds ad groups to a given campaign.

To get ad groups, run get_ad_groups.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README..

"""


import uuid

from googleads import adwords


CAMPAIGN_ID = 'INSERT_CAMPAIGN_ID_HERE'


def main(client, campaign_id):
  # Initialize appropriate service.
  ad_group_service = client.GetService('AdGroupService', version='v201502')

  # Construct operations and add ad groups.
  operations = [{
      'operator': 'ADD',
      'operand': {
          'campaignId': campaign_id,
          'name': 'Earth to Mars Cruises #%s' % uuid.uuid4(),
          'status': 'ENABLED',
          'biddingStrategyConfiguration': {
              'bids': [
                  {
                      'xsi_type': 'CpcBid',
                      'bid': {
                          'microAmount': '1000000'
                      },
                  }
              ]
          },
          'settings': [
              {
                  # Targeting restriction settings - these settings only affect
                  # serving for the Display Network.
                  'xsi_type': 'TargetingSetting',
                  'details': [
                      # Restricting to serve ads that match your ad group
                      # placements. This is equivalent to choosing
                      # "Target and bid" in the UI.
                      {
                          'xsi_type': 'TargetingSettingDetail',
                          'criterionTypeGroup': 'PLACEMENT',
                          'targetAll': 'false',
                      },
                      # Using your ad group verticals only for bidding. This is
                      # equivalent to choosing "Bid only" in the UI.
                      {
                          'xsi_type': 'TargetingSettingDetail',
                          'criterionTypeGroup': 'VERTICAL',
                          'targetAll': 'true',
                      },
                  ]
              }
          ]
      }
  }, {
      'operator': 'ADD',
      'operand': {
          'campaignId': campaign_id,
          'name': 'Earth to Venus Cruises #%s' % uuid.uuid4(),
          'status': 'ENABLED',
          'biddingStrategyConfiguration': {
              'bids': [
                  {
                      'xsi_type': 'CpcBid',
                      'bid': {
                          'microAmount': '1000000'
                      }
                  }
              ]
          }
      }
  }]
  ad_groups = ad_group_service.mutate(operations)

  # Display results.
  for ad_group in ad_groups['value']:
    print ('Ad group with name \'%s\' and id \'%s\' was added.'
           % (ad_group['name'], ad_group['id']))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, CAMPAIGN_ID)
