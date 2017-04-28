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

"""Gets all available campaign criterion bid modifier landscapes for a campaign.

To get campaigns, run basic_operations/get_campaigns.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

from googleads import adwords


CAMPAIGN_ID = 'INSERT_CAMPAIGN_ID_HERE'
PAGE_SIZE = 500


def main(client, campaign_id):
  # Initialize appropriate service.
  data_service = client.GetService('DataService', version='v201609')

  # Get all the campaigns for this account.
  selector = {
      'fields': ['CampaignId', 'CriterionId', 'StartDate', 'EndDate',
                 'BidModifier', 'LocalClicks', 'LocalCost', 'LocalImpressions',
                 'TotalLocalClicks', 'TotalLocalCost', 'TotalLocalImpressions',
                 'RequiredBudget'],
      'paging': {
          'startIndex': 0,
          'numberResults': PAGE_SIZE
      },
      'predicates': [{
          'field': 'CampaignId', 'operator': 'IN', 'values': [campaign_id]
      }]
  }

  # Set initial values.
  offset = 0
  more_pages = True

  while more_pages is True:
    num_landscape_points = 0
    page = data_service.getCampaignCriterionBidLandscape(selector)

    # Display results.
    if 'entries' in page:
      for bid_modifier_landscape in page['entries']:
        num_landscape_points = 0
        print ('Found campaign-level criterion bid modifier landscapes for '
               'criterion with ID "%d", start date "%s", end date "%s", and '
               'landscape points:') % (bid_modifier_landscape['criterionId'],
                                       bid_modifier_landscape['startDate'],
                                       bid_modifier_landscape['endDate'])
        for landscape_point in bid_modifier_landscape['landscapePoints']:
          num_landscape_points += 1
          print ('\tbid modifier: %f, clicks: %d, cost: %d, impressions: %d, '
                 'total clicks: %d, total cost: %d, total impressions: %d, '
                 'and required budget: %f') % (
                     landscape_point['bidModifier'], landscape_point['clicks'],
                     landscape_point['cost']['microAmount'],
                     landscape_point['impressions'],
                     landscape_point['totalLocalClicks'],
                     landscape_point['totalLocalCost']['microAmount'],
                     landscape_point['totalLocalImpressions'],
                     landscape_point['requiredBudget']['microAmount'])
    else:
      print 'No bid modifier landscapes found.'

    # Need to increment by the total # of landscape points within the page.
    offset += num_landscape_points
    selector['paging']['startIndex'] = str(offset)
    more_pages = offset < int(page['totalNumEntries'])


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, CAMPAIGN_ID)
