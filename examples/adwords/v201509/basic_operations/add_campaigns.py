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

"""This example adds campaigns.

To get campaigns, run get_campaigns.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


import datetime
import uuid
from googleads import adwords


def main(client):
  # Initialize appropriate services.
  campaign_service = client.GetService('CampaignService', version='v201509')
  budget_service = client.GetService('BudgetService', version='v201509')

  # Create a budget, which can be shared by multiple campaigns.
  budget = {
      'name': 'Interplanetary budget #%s' % uuid.uuid4(),
      'amount': {
          'microAmount': '50000000'
      },
      'deliveryMethod': 'STANDARD',
      'period': 'DAILY'
  }

  budget_operations = [{
      'operator': 'ADD',
      'operand': budget
  }]

  # Add the budget.
  budget_id = budget_service.mutate(budget_operations)['value'][0][
      'budgetId']

  # Construct operations and add campaigns.
  operations = [{
      'operator': 'ADD',
      'operand': {
          'name': 'Interplanetary Cruise #%s' % uuid.uuid4(),
          'status': 'PAUSED',
          'advertisingChannelType': 'SEARCH',
          'biddingStrategyConfiguration': {
              'biddingStrategyType': 'MANUAL_CPC',
          },
          'endDate': (datetime.datetime.now() +
                      datetime.timedelta(365)).strftime('%Y%m%d'),
          # Note that only the budgetId is required
          'budget': {
              'budgetId': budget_id
          },
          'networkSetting': {
              'targetGoogleSearch': 'true',
              'targetSearchNetwork': 'true',
              'targetContentNetwork': 'false',
              'targetPartnerSearchNetwork': 'false'
          },
          # Optional fields
          'startDate': (datetime.datetime.now() +
                        datetime.timedelta(1)).strftime('%Y%m%d'),
          'adServingOptimizationStatus': 'ROTATE',
          'frequencyCap': {
              'impressions': '5',
              'timeUnit': 'DAY',
              'level': 'ADGROUP'
          },
          'settings': [
              {
                  'xsi_type': 'GeoTargetTypeSetting',
                  'positiveGeoTargetType': 'DONT_CARE',
                  'negativeGeoTargetType': 'DONT_CARE'
              }
          ]
      }
  }, {
      'operator': 'ADD',
      'operand': {
          'name': 'Interplanetary Cruise banner #%s' % uuid.uuid4(),
          'status': 'PAUSED',
          'biddingStrategyConfiguration': {
              'biddingStrategyType': 'MANUAL_CPC'
          },
          'endDate': (datetime.datetime.now() +
                      datetime.timedelta(365)).strftime('%Y%m%d'),
          # Note that only the budgetId is required
          'budget': {
              'budgetId': budget_id
          },
          'advertisingChannelType': 'DISPLAY'
      }
  }]
  campaigns = campaign_service.mutate(operations)

  # Display results.
  for campaign in campaigns['value']:
    print ('Campaign with name \'%s\' and id \'%s\' was added.'
           % (campaign['name'], campaign['id']))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client)
