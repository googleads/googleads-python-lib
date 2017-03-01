#!/usr/bin/python
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

"""This example adds various types of targeting criteria to a given campaign.

To get campaigns, run get_campaigns.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

from googleads import adwords


CAMPAIGN_ID = 'INSERT_CAMPAIGN_ID_HERE'
# Replace the value below with the ID of a feed that has been configured for
# location targeting, meaning it has an ENABLED FeedMapping with criterionType
# of 77. Feeds linked to a GMB account automatically have this FeedMapping.
# If you don't have such a feed, set this value to None.
LOCATION_FEED_ID = 'INSERT_LOCATION_FEED_ID_HERE'


def main(client, campaign_id, location_feed_id=None):
  # Initialize appropriate service.
  campaign_criterion_service = client.GetService(
      'CampaignCriterionService', version='v201702')

  # Create locations. The IDs can be found in the documentation or retrieved
  # with the LocationCriterionService.
  california = {
      'xsi_type': 'Location',
      'id': '21137'
  }
  mexico = {
      'xsi_type': 'Location',
      'id': '2484'
  }

  # Create languages. The IDs can be found in the documentation or retrieved
  # with the ConstantDataService.
  english = {
      'xsi_type': 'Language',
      'id': '1000'
  }
  spanish = {
      'xsi_type': 'Language',
      'id': '1003'
  }

  # Create a negative campaign criterion operation.
  negative_campaign_criterion_operand = {
      'xsi_type': 'NegativeCampaignCriterion',
      'campaignId': campaign_id,
      'criterion': {
          'xsi_type': 'Keyword',
          'matchType': 'BROAD',
          'text': 'jupiter cruise'
      }
  }
  criteria = [california, mexico, english, spanish]
  if location_feed_id:
      # Distance targeting. Area of 10 miles around targets above.
    criteria.append({
        'xsi_type': 'LocationGroups',
        'feedId': location_feed_id,
        'matchingFunction': {
            'operator': 'IDENTITY',
            'lhsOperand': [{
                'xsi_type': 'LocationExtensionOperand',
                'radius': {
                    'xsi_type': 'ConstantOperand',
                    'type': 'DOUBLE',
                    'unit': 'MILES',
                    'doubleValue': 10
                }
            }]
        }
    })
  # Create operations
  operations = []
  for criterion in criteria:
    operations.append({
        'operator': 'ADD',
        'operand': {
            'campaignId': campaign_id,
            'criterion': criterion
        }
    })
  # Add the negative campaign criterion.
  operations.append({
      'operator': 'ADD',
      'operand': negative_campaign_criterion_operand
  })

  # Make the mutate request.
  result = campaign_criterion_service.mutate(operations)

  # Display the resulting campaign criteria.
  for campaign_criterion in result['value']:
    print ('Campaign criterion with campaign id \'%s\', criterion id \'%s\', '
           'and type \'%s\' was added.'
           % (campaign_criterion['campaignId'],
              campaign_criterion['criterion']['id'],
              campaign_criterion['criterion']['type']))

if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, CAMPAIGN_ID, LOCATION_FEED_ID)
