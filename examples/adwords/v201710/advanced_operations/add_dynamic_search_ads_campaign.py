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

"""This example adds a Dynamic Search Ads campaign.

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
  budget = _CreateBudget(client)
  campaign_id = _CreateCampaign(client, budget)
  ad_group_id = _CreateAdGroup(client, campaign_id)
  _CreateExpandedDSA(client, ad_group_id)
  _AddWebPageCriteria(client, ad_group_id)

  print 'Dynamic Search Ads campaign setup is complete.'


def _CreateBudget(client):
  """Creates the budget.

  Args:
    client: an AdWordsClient instance.

  Returns:
    a suds.sudsobject.Object representation of the created budget.
  """
  budget_service = client.GetService('BudgetService', version='v201710')

  # Create the campaign budget
  operation = {
      'operand': {
          'name': 'Interplanetary Cruise Budget #%d' % uuid.uuid4(),
          'deliveryMethod': 'STANDARD',
          'amount': {
              'microAmount': 500000
          }
      },
      'operator': 'ADD'
  }

  budget = budget_service.mutate([operation])['value'][0]

  print 'Budget with ID "%d" and name "%s" was created.' % (
      budget['budgetId'], budget['name'])

  return budget


def _CreateCampaign(client, budget):
  """Creates the campaign.

  Args:
    client: an AdWordsClient instance.
    budget: a suds.sudsobject.Object representation of a created budget.

  Returns:
    An integer campaign ID.
  """
  campaign_service = client.GetService('CampaignService')

  operations = [{
      'operator': 'ADD',
      'operand': {
          'name': 'Interplanetary Cruise #%d' % uuid.uuid4(),
          # Recommendation: Set the campaign to PAUSED when creating it to
          # prevent the ads from immediately serving. Set to ENABLED once you've
          # added targeting and the ads are ready to serve.
          'status': 'PAUSED',
          'advertisingChannelType': 'SEARCH',
          'biddingStrategyConfiguration': {
              'biddingStrategyType': 'MANUAL_CPC',
          },
          'budget': budget,
          # Required: Set the campaign's Dynamic Search Ad settings.
          'settings': [{
              'xsi_type': 'DynamicSearchAdsSetting',
              # Required: Set the domain name and language.
              'domainName': 'example.com',
              'languageCode': 'en'
          }],
          # Optional: Set the start date.
          'startDate': (datetime.datetime.now() +
                        datetime.timedelta(1)).strftime('%Y%m%d'),
          # Optional: Set the end date.
          'endDate': (datetime.datetime.now() +
                      datetime.timedelta(365)).strftime('%Y%m%d'),
      }
  }]

  campaign = campaign_service.mutate(operations)['value'][0]
  campaign_id = campaign['id']

  print 'Campaign with ID "%d" and name "%s" was added.' % (
      campaign_id, campaign['name'])

  return campaign_id


def _CreateAdGroup(client, campaign_id):
  """Creates an ad group.

  Args:
    client: an AdWordsClient instance.
    campaign_id: an integer campaign ID.

  Returns:
    An integer ad group ID.
  """
  ad_group_service = client.GetService('AdGroupService')

  operations = [{
      'operator': 'ADD',
      'operand': {
          'campaignId': campaign_id,
          'adGroupType': 'SEARCH_DYNAMIC_ADS',
          'name': 'Earth to Mars Cruises #%d' % uuid.uuid4(),
          'status': 'PAUSED',
          'biddingStrategyConfiguration': {
              'bids': [{
                  'xsi_type': 'CpcBid',
                  'bid': {
                      'microAmount': '3000000'
                  },
              }]
          }
      }
  }]

  ad_group = ad_group_service.mutate(operations)['value'][0]
  ad_group_id = ad_group['id']

  print 'Ad group with ID "%d" and name "%s" was created.' % (
      ad_group_id, ad_group['name'])

  return ad_group_id


def _CreateExpandedDSA(client, ad_group_id):
  """Creates the expanded Dynamic Search Ad.

  Args:
    client: an AdwordsClient instance.
    ad_group_id: an integer ID of the ad group in which the DSA is added.
  """
  # Get the AdGroupAdService.
  ad_group_ad_service = client.GetService('AdGroupAdService')

  # Create the operation
  operations = [{
      'operator': 'ADD',
      'operand': {
          'xsi_type': 'AdGroupAd',
          'adGroupId': ad_group_id,
          # Create the expanded dynamic search ad. This ad will have its
          # headline and final URL auto-generated at serving time according to
          # domain name specific information provided by DynamicSearchAdsSetting
          # at the campaign level.
          'ad': {
              'xsi_type': 'ExpandedDynamicSearchAd',
              # Set the ad description.
              'description': 'Buy your tickets now!'
          },
          # Optional: Set the status.
          'status': 'PAUSED',
      }
  }]

  # Create the ad.
  ad = ad_group_ad_service.mutate(operations)['value'][0]['ad']

  # Display the results.
  print ('Expanded dynamic search ad with ID "%d" and description "%s" was '
         'added' % (ad['id'], ad['description']))


def _AddWebPageCriteria(client, ad_group_id):
  """Adds a web page criterion to target Dynamic Search Ads.

  Args:
    client: an AdWordsClient instance.
    ad_group_id: an integer ID of the ad group the criteria is being added to.
  """
  ad_group_criterion_service = client.GetService('AdGroupCriterionService',
                                                 version='v201710')

  operations = [{
      'operator': 'ADD',
      # Create biddable ad group criterion.
      'operand': {
          'xsi_type': 'BiddableAdGroupCriterion',
          'adGroupId': ad_group_id,
          # Create a webpage criterion for special offers for children.
          'criterion': {
              'xsi_type': 'Webpage',
              'parameter': {
                  'criterionName': 'Special offers for children.',
                  'conditions': [
                      {
                          'operand': 'URL',
                          'argument': '/marscruise/children'
                      },
                      {
                          'operand': 'PAGE_TITLE',
                          'argument': 'Special Offer'
                      }
                  ]
              }
          },
          'userStatus': 'PAUSED',
          # Optional: set a custom bid.
          'biddingStrategyConfiguration': {
              'bids': [{
                  'xsi_type': 'CpcBid',
                  'bid': {
                      'microAmount': 10000000L
                  }
              }]
          }
      }
  }]

  criterion = ad_group_criterion_service.mutate(operations)['value'][0]

  print 'Webpage criterion with ID "%d" was added to ad group ID "%d".' % (
      criterion['criterion']['id'], criterion['adGroupId'])


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client)
