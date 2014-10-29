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

"""This example retrieves keywords that are related to a given keyword.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: TargetingIdeaService.get
Api: AdWordsOnly
"""

__author__ = ('api.kwinter@gmail.com (Kevin Winter)'
              'Joseph DiLallo')

from googleads import adwords


PAGE_SIZE = 100


def main(client):
  # Initialize appropriate service.
  targeting_idea_service = client.GetService(
      'TargetingIdeaService', version='v201406')

  # Construct selector object and retrieve related keywords.
  offset = 0
  selector = {
      'searchParameters': [
          {
              'xsi_type': 'RelatedToQuerySearchParameter',
              'queries': ['space cruise']
          },
          {
              # Language setting (optional).
              # The ID can be found in the documentation:
              #  https://developers.google.com/adwords/api/docs/appendix/languagecodes
              'xsi_type': 'LanguageSearchParameter',
              'languages': [{'id': '1000'}]
          }
      ],
      'ideaType': 'KEYWORD',
      'requestType': 'IDEAS',
      'requestedAttributeTypes': ['KEYWORD_TEXT', 'SEARCH_VOLUME',
                                  'CATEGORY_PRODUCTS_AND_SERVICES'],
      'paging': {
          'startIndex': str(offset),
          'numberResults': str(PAGE_SIZE)
      }
  }
  more_pages = True
  while more_pages:
    page = targeting_idea_service.get(selector)

    # Display results.
    if 'entries' in page:
      for result in page['entries']:
        attributes = {}
        for attribute in result['data']:
          attributes[attribute['key']] = attribute['value']
        print ('Keyword with \'%s\' text and average monthly search volume '
               '\'%s\' was found with Products and Services categories: %s.'
               % (attributes['KEYWORD_TEXT'],
                  attributes['SEARCH_VOLUME'],
                  attributes['CATEGORY_PRODUCTS_AND_SERVICES']))
      print
    else:
      print 'No related keywords were found.'
    offset += PAGE_SIZE
    selector['paging']['startIndex'] = str(offset)
    more_pages = offset < int(page['totalNumEntries'])


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client)
