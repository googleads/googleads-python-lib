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

"""Attaches a new shared list of negative broad match keywords to a campaign.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


import uuid

from googleads import adwords
from googleads import errors


CAMPAIGN_ID = 'INSERT_CAMPAIGN_ID_HERE'


def main(client, campaign_id):
  # Initialize appropriate services.
  shared_set_service = client.GetService('SharedSetService', version='v201506')
  shared_criterion_service = client.GetService('SharedCriterionService',
                                               version='v201506')
  campaign_shared_set_service = client.GetService('CampaignSharedSetService',
                                                  version='v201506')

  # Keywords to create a shared set of.
  keywords = ['mars cruise', 'mars hotels']
  # Create shared negative keyword set.
  shared_set = {
      'name': 'API Negative keyword list - %d' % uuid.uuid4(),
      'type': 'NEGATIVE_KEYWORDS'
  }

  # Add shared set.
  operations = [{
      'operator': 'ADD',
      'operand': shared_set
  }]

  response = shared_set_service.mutate(operations)

  if response and response['value']:
    shared_set = response['value'][0]
    shared_set_id = shared_set['sharedSetId']

    print 'Shared set with ID %d and name "%s" was successfully added.' % (
        shared_set_id, shared_set['name']
    )
  else:
    raise errors.GoogleAdsError('No shared set was added.')

    # Add negative keywords to shared set.
  shared_criteria = [
      {
          'criterion': {
              'xsi_type': 'Keyword',
              'text': keyword,
              'matchType': 'BROAD'
          },
          'negative': True,
          'sharedSetId': shared_set_id
      } for keyword in keywords
  ]

  operations = [
      {
          'operator': 'ADD',
          'operand': criterion
      } for criterion in shared_criteria
  ]

  response = shared_criterion_service.mutate(operations)

  if 'value' in response:
    for shared_criteria in response['value']:
      print 'Added shared criterion ID %d "%s" to shared set with ID %d.' % (
          shared_criteria['criterion']['id'],
          shared_criteria['criterion']['text'],
          shared_criteria['sharedSetId']
      )
  else:
    raise errors.GoogleAdsError('No shared keyword was added.')

    # Attach the articles to the campaign.
  campaign_set = {
      'campaignId': campaign_id,
      'sharedSetId': shared_set_id
  }

  operations = [
      {
          'operator': 'ADD',
          'operand': campaign_set
      }
  ]

  response = campaign_shared_set_service.mutate(operations)

  if 'value' in response:
    print 'Shared set ID %d was attached to campaign ID %d' % (
        response['value'][0]['sharedSetId'], response['value'][0]['campaignId']
    )
  else:
    raise errors.GoogleAdsError('No campaign shared set was added.')


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, CAMPAIGN_ID)
