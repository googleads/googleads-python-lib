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

"""This example adds a Universal App campaign.

To get campaigns, run get_campaigns.py. To upload image assets for this
campaign, run upload_image.py.

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
  campaign_service = client.GetService('CampaignService', version='v201702')

  budget_id = CreateBudget(client)

  # Create the Universal App campaign.
  universal_app_campaign = {
      'name': 'Interplanetary Cruise App #%s' % uuid.uuid4(),
      # Recommendation: Set the campaign to PAUSED when creating it to stop the
      # ads from immediately serving. Set to ENABLED once you've added targeting
      # and the ads are ready to serve.
      'status': 'PAUSED',
      'advertisingChannelType': 'MULTI_CHANNEL',
      'advertisingChannelSubType': 'UNIVERSAL_APP_CAMPAIGN',
      # Set the campaign's bidding strategy. Universal app campaigns only
      # support TARGET_CPA bidding strategy.
      'biddingStrategyConfiguration': {
          # Set the target CPA to $1 / app install.
          'biddingScheme': {
              'xsi_type': 'TargetCpaBiddingScheme',
              'targetCpa': {
                  'microAmount': '1000000'
              }
          },
          'biddingStrategyType': 'TARGET_CPA'
      },
      # Note that only the budgetId is required
      'budget': {
          'budgetId': budget_id
      },
      # Optional fields
      'startDate': (datetime.datetime.now() +
                    datetime.timedelta(1)).strftime('%Y%m%d'),
      'endDate': (datetime.datetime.now() +
                  datetime.timedelta(365)).strftime('%Y%m%d'),
  }

  universal_app_campaign['settings'] = [
      # Set the campaign's assets and ad text ideas. These values will
      # be used to generate ads.
      {
          'xsi_type': 'UniversalAppCampaignSetting',
          'appId': 'com.labpixies.colordrips',
          'description1': 'A cool puzzle game',
          'description2': 'Remove connected blocks',
          'description3': '3 difficulty levels',
          'description4': '4 colorful fun skins',
          # Optional: You can set up to 10 image assets for your campaign.
          # See upload_image.py for an example on how to upload images.
          #
          # 'imageMediaIds': [INSERT_IMAGE_MEDIA_ID(s)_HERE]
      }
  ]

  # Optimize this campaign for getting new users for your app.
  universal_app_campaign_setting = universal_app_campaign['settings'][0]
  universal_app_campaign_setting['universalAppBiddingStrategyGoalType'] = (
      'OPTIMIZE_FOR_INSTALL_CONVERSION_VOLUME')

  # Optional: If you select the OPTIMIZE_FOR_IN_APP_CONVERSION_VOLUME goal type,
  # then also specify your in-app conversion types so AdWords can focus your
  # campaign on people who are most likely to complete the corresponding in-app
  # actions.
  #
  # Conversions type IDs can be retrieved using ConversionTrackerService.get.
  # universal_app_campaign['selectiveOptimization'] = {
  #     'conversionTypeIds': [INSERT_CONVERSION_TYPE_ID(s)_HERE]
  # }

  # Optional: Set the campaign settings for Advanced location options.
  universal_app_campaign['settings'].append({
      'xsi_type': 'GeoTargetTypeSetting',
      'positiveGeoTargetType': 'DONT_CARE',
      'negativeGeoTargetType': 'DONT_CARE'
  })

  # Construct operations and add campaigns.
  operations = [{
      'operator': 'ADD',
      'operand': universal_app_campaign
  }]

  campaigns = campaign_service.mutate(operations)['value']

  # Display results.
  if campaigns:
    for campaign in campaigns:
      print ('Universal App Campaign with name "%s" and id "%s" was added.'
             % (campaign['name'], campaign['id']))
      # Optional: Set the campaign's location and language targeting. No other
      # targeting criteria can be used for Universal App campaigns.
      SetCampaignTargetingCriteria(client, campaign)
  else:
    print 'No Universal App campaigns were added.'


def CreateBudget(client):
  """Creates a budget and returns its budgetId.

  Args:
    client: An AdWordsClient instance.

  Returns:
    An int budgetId for the created Budget.
  """
  budget_service = client.GetService('BudgetService', version='v201702')

  # Create a budget.
  budget = {
      'name': 'Interplanetary Cruise App Budget #%s' % uuid.uuid4(),
      'amount': {
          'microAmount': '50000000'
      },
      'deliveryMethod': 'STANDARD',
      'isExplicitlyShared': False
  }

  budget_operations = [{
      'operator': 'ADD',
      'operand': budget
  }]

  # Create the budget and return its ID.
  budget_id = budget_service.mutate(budget_operations)['value'][0]['budgetId']
  # [END createBudget] MOE_strip_line

  return budget_id


def SetCampaignTargetingCriteria(client, campaign):
  """Sets targeting criteria for the given campaign.

  Args:
    client: An AdWordsClient instance.
    campaign: A suds object representing the campaign we wish to attach
      targeting criteria.
  """
  campaign_criterion_service = client.GetService('CampaignCriterionService')

  # Create locations. The IDs can be found in the documentation or retrieved
  # with the LocationCriterionService.
  criteria = [
      {
          'xsi_type': 'Location',
          'id': 21137  # California
      },
      {
          'xsi_type': 'Location',
          'id': 2484  # Mexico
      },
      {
          'xsi_type': 'Language',
          'id': 1000  # English
      },
      {
          'xsi_type': 'Language',
          'id': 1003  # Spanish
      }
  ]

  operations = [{
      'operator': 'ADD',
      'operand': {
          'campaignId': campaign['id'],
          'criterion': criterion
      }
  } for criterion in criteria]

  response = campaign_criterion_service.mutate(operations)

  if response and 'value' in response:
    # Display the added campaign targets.
    for criterion in response['value']:
      print ('Campaign criteria of type "%s" and id "%s" was added.'
             % (criterion['criterion']['type'],
                criterion['criterion']['id']))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client)
