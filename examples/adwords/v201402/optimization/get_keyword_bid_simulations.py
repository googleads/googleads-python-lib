#!/usr/bin/python
#
# Copyright 2014 Google Inc. All Rights Reserved.
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

"""This example gets a bid landscape for an ad group and a criterion.

To get ad groups, run get_ad_groups.py. To get criteria, run get_keywords.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: BidLandscapeService.getBidLandscape
Api: AdWordsOnly
"""

__author__ = ('api.kwinter@gmail.com (Kevin Winter)'
              'Joseph DiLallo')

from googleads import adwords


AD_GROUP_ID = 'INSERT_AD_GROUP_ID_HERE'
CRITERION_ID = 'INSERT_CRITERION_ID_HERE'


def main(client, ad_group_id, criterion_id):
  # Initialize appropriate service.
  data_service = client.GetService('DataService', version='v201402')

  # Construct bid landscape selector object and retrieve bid landscape.
  selector = {
      'fields': ['AdGroupId', 'CriterionId', 'StartDate', 'EndDate', 'Bid',
                 'LocalClicks', 'LocalCost', 'MarginalCpc', 'LocalImpressions'],
      'predicates': [
          {
              'field': 'AdGroupId',
              'operator': 'EQUALS',
              'values': [ad_group_id]
          },
          {
              'field': 'CriterionId',
              'operator': 'EQUALS',
              'values': [criterion_id]
          }
      ]
  }
  bid_landscapes = data_service.getCriterionBidLandscape(selector)

  # Display results.
  if 'entries' in bid_landscapes:
    for bid_landscape in bid_landscapes['entries']:
      if bid_landscape['BidLandscape.Type'] == 'CriterionBidLandscape':
        print ('Criterion bid landscape with ad group id \'%s\', criterion id '
               '\'%s\', start date \'%s\', end date \'%s\', with landscape '
               'points was found:'
               % (bid_landscape['adGroupId'], bid_landscape['criterionId'],
                  bid_landscape['startDate'], bid_landscape['endDate']))
        for bid_landscape_point in bid_landscape['landscapePoints']:
          print ('  bid: %s => clicks: %s, cost: %s, marginalCpc: %s, '
                 'impressions: %s'
                 % (bid_landscape_point['bid']['microAmount'],
                    bid_landscape_point['clicks'],
                    bid_landscape_point['cost']['microAmount'],
                    bid_landscape_point['marginalCpc']['microAmount'],
                    bid_landscape_point['impressions']))
  else:
    print 'No bid landscapes found.'


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, AD_GROUP_ID, CRITERION_ID)
