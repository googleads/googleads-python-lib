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

"""Retrieves the ad group level bid modifiers for a campaign.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

from googleads import adwords


PAGE_SIZE = 500


def main(client):
  # Initialize appropriate service.
  ad_group_bid_modifier_service = client.GetService(
      'AdGroupBidModifierService', version='v201509')

  # Get all ad group bid modifiers for the campaign.
  selector = {
      'fields': ['CampaignId', 'AdGroupId', 'BidModifier', 'Id'],
      'paging': {
          'startIndex': '0',
          'numberResults': str(PAGE_SIZE)
      }
  }

  # Set initial values.
  offset, page = 0, {}
  more_results = True

  while more_results:
    page = ad_group_bid_modifier_service.get(selector)
    if page['entries']:
      for modifier in page['entries']:
        value = (modifier['bidModifier'] if 'bidModifier' in modifier
                 else 'unset')
        print ('Campaign ID %s, AdGroup ID %s, Criterion ID %s has ad group '
               'level modifier: %s' %
               (modifier['campaignId'], modifier['adGroupId'],
                modifier['criterion']['id'], value))

      # Increment values to request the next page.
      offset += PAGE_SIZE
      selector['paging']['startIndex'] = str(offset)
    else:
      print 'No ad group bid modifiers returned.'
    more_results = int(page['totalNumEntries']) > offset


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client)
