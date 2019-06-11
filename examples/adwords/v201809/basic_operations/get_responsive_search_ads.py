#!/usr/bin/env python
#
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This example gets non-removed responsive search ads in a specified ad group.

To add responsive search ads, run add_responsive_search_ad.py. To get ad groups,
run get_ad_groups.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

from googleads import adwords


PAGE_SIZE = 500
AD_GROUP_ID = 'INSERT_AD_GROUP_ID_HERE'


def main(client, ad_group_id):
  # Initialize appropriate service.
  ad_group_ad_service = client.GetService('AdGroupAdService', version='v201809')

  # Construct selector and get all ads for a given ad group.
  offset = 0
  selector = {
      'fields': ['Id', 'Status', 'ResponsiveSearchAdHeadlines',
                 'ResponsiveSearchAdDescriptions'],
      'predicates': [
          {
              'field': 'AdGroupId',
              'operator': 'EQUALS',
              'values': [ad_group_id]
          },
          {
              'field': 'AdType',
              'operator': 'EQUALS',
              'values': ['RESPONSIVE_SEARCH_AD']
          }
      ],
      'paging': {
          'startIndex': str(offset),
          'numberResults': str(PAGE_SIZE)
      },
      'ordering': [
          {
              'field': 'Id',
              'sortOrder': 'ASCENDING'
          }
      ]
  }

  more_pages = True
  while more_pages:
    page = ad_group_ad_service.get(selector)

    # Display results.
    if 'entries' in page:
      for ad_group_ad in page['entries']:
        ad = ad_group_ad['ad']
        print('Responsive search ad with status %s and id "%d" was found.\n'
              'Headlines:\n%s\n'
              'Descriptions:\n%s'
              % (ad_group_ad['status'], ad['id'],
                  '\n'.join(['\t%s (pinned to %s)' %
                             (headline['asset']['assetText'],
                              headline['pinnedField'])
                             for headline in ad['headlines']]),
                  '\n'.join(['\t%s (pinned to %s)' %
                             (headline['asset']['assetText'],
                              headline['pinnedField'])
                             for headline in ad['descriptions']])))
    else:
      print('No ads were found.')
    offset += PAGE_SIZE
    selector['paging']['startIndex'] = str(offset)
    more_pages = offset < int(page['totalNumEntries'])


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, AD_GROUP_ID)
