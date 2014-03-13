#!/usr/bin/python
#
# Copyright 2013 Google Inc. All Rights Reserved.
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

"""This example retrieves placements that are related to a given placement.

Tags: TargetingIdeaService.get
"""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

from googleads import adwords


PAGE_SIZE = 100


def main(client):
  # Initialize appropriate service.
  targeting_idea_service = client.GetService(
      'TargetingIdeaService', version='v201402')

  # Construct selector object and retrieve related placements.
  offset = 0
  url = 'mars.google.com'
  selector = {
      'searchParameters': [{
          'xsi_type': 'RelatedToUrlSearchParameter',
          'urls': [url]
      }],
      'ideaType': 'PLACEMENT',
      'requestType': 'IDEAS',
      'requestedAttributeTypes': ['CRITERION'],
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
        result = result['data'][0]['value']
        print ('Placement with url \'%s\' was found.'
               % (result['value']['url']))
      print
      print ('Total placements found related to \'%s\': %s'
             % (url, page['totalNumEntries']))
    else:
      print 'No placements found related to \'%s\'.' % url
    offset += PAGE_SIZE
    selector['paging']['startIndex'] = str(offset)
    more_pages = offset < int(page['totalNumEntries'])


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client)
