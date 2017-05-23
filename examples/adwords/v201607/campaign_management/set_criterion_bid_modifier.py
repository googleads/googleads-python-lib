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

"""This example sets a bid modifier for the mobile platform on given campaign.

To get campaigns, run get_campaigns.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""
from googleads import adwords


CAMPAIGN_ID = 'INSERT_CAMPAIGN_ID_HERE'
BID_MODIFIER = '1.5'


def main(client, campaign_id, bid_modifier):
  # Initialize appropriate service.
  campaign_criterion_service = client.GetService(
      'CampaignCriterionService', version='v201607')

  # Create mobile platform.The ID can be found in the documentation.
  # https://developers.google.com/adwords/api/docs/appendix/platforms
  mobile = {
      'xsi_type': 'Platform',
      'id': '30001'
  }

  # Create campaign criterion with modified bid.
  campaign_criterion = {
      'campaignId': campaign_id,
      'criterion': mobile,
      'bidModifier': bid_modifier
  }

  # Create operations.
  operations = [
      {
          'operator': 'SET',
          'operand': campaign_criterion
      }
  ]

  # Make the mutate request.
  result = campaign_criterion_service.mutate(operations)

  # Display the resulting campaign criteria.
  for campaign_criterion in result['value']:
    print ('Campaign criterion with campaign id \'%s\' and criterion id \'%s\' '
           'was updated with bid modifier \'%s\'.'
           % (campaign_criterion['campaignId'],
              campaign_criterion['criterion']['id'],
              campaign_criterion['bidModifier']))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, CAMPAIGN_ID, BID_MODIFIER)
