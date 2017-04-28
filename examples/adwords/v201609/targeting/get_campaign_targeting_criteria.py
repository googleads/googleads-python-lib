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

"""This example illustrates how to retrieve all the campaign targets.

To set campaign targets, run add_campaign_targeting_criteria.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

from googleads import adwords


PAGE_SIZE = 500


def main(client):
  # Initialize appropriate service.
  campaign_criterion_service = client.GetService(
      'CampaignCriterionService', version='v201609')

  # Construct selector and get all campaign targets.
  offset = 0
  selector = {
      'fields': ['CampaignId', 'Id', 'CriteriaType', 'PlatformName',
                 'LanguageName', 'LocationName', 'KeywordText'],
      'predicates': [{
          'field': 'CriteriaType',
          'operator': 'IN',
          'values': ['KEYWORD', 'LANGUAGE', 'LOCATION', 'PLATFORM']
      }],
      'paging': {
          'startIndex': str(offset),
          'numberResults': str(PAGE_SIZE)
      }
  }
  more_pages = True
  while more_pages:
    page = campaign_criterion_service.get(selector)

    # Display results.
    if 'entries' in page:
      for campaign_criterion in page['entries']:
        negative = ''
        if (campaign_criterion['CampaignCriterion.Type']
            == 'NegativeCampaignCriterion'):
          negative = 'Negative '
        criterion = campaign_criterion['criterion']
        criteria = (criterion['text'] if 'text' in criterion else
                    criterion['platformName'] if 'platformName' in criterion
                    else criterion['name'] if 'name' in criterion else
                    criterion['locationName'] if 'locationName' in criterion
                    else None)
        print ('%sCampaign Criterion found for Campaign ID %s with type %s and '
               'criteria "%s".' % (negative, campaign_criterion['campaignId'],
                                   criterion['type'], criteria))
    else:
      print 'No campaign targets were found.'
    offset += PAGE_SIZE
    selector['paging']['startIndex'] = str(offset)
    more_pages = offset < int(page['totalNumEntries'])


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client)
