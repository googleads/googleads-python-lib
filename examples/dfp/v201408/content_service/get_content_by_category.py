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

"""This code example gets all active content categorized as a "comedy" using the
network's content browse custom targeting key.

This feature is only available to DFP video publishers.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: ContentService.getContentByStatement
"""

__author__ = ('Nicholas Chen',
              'Joseph DiLallo')

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  content_service = client.GetService('ContentService', version='v201408')
  network_service = client.GetService('NetworkService', version='v201408')
  custom_targeting_service = client.GetService(
      'CustomTargetingService', version='v201408')

  # Get the network's content browse custom targeting key.
  network = network_service.getCurrentNetwork()
  key_id = network['contentBrowseCustomTargetingKeyId']

  # Create a statement to select the categories matching the name comedy.
  values = [
      {
          'key': 'contentBrowseCustomTargetingKeyId',
          'value': {
              'xsi_type': 'NumberValue',
              'value': key_id
          }
      },
      {
          'key': 'category',
          'value': {
              'xsi_type': 'TextValue',
              'value': 'comedy'
          }
      }
  ]
  category_filter_query = ('WHERE customTargetingKeyId = '
                           ':contentBrowseCustomTargetingKeyId and name = '
                           ':category')
  category_filter_statement = dfp.FilterStatement(
      category_filter_query, values, 1)

  # Get categories matching the filter statement.
  response = custom_targeting_service.getCustomTargetingValuesByStatement(
      category_filter_statement.ToStatement())

  # Get the custom targeting value ID for the comedy category.
  if 'results' in response:
    category_custom_targeting_value_id = (response['results']['id'])

    # Create a statement to select the active content.
    content_values = [
        {
            'key': 'status',
            'value': {
                'xsi_type': 'TextValue',
                'value': 'ACTIVE'
            }
        }
    ]
    content_query = 'WHERE status = :status'
    content_statement = dfp.FilterStatement(content_query, content_values)

    while True:
      # Get the content by statement and custom targeting value.
      response = content_service.getContentByStatementAndCustomTargetingValue(
          content_statement.ToStatement(),
          category_custom_targeting_value_id)
      if 'results' in response:
        # Display results.
        for content_item in response['results']:
          print ('Content with id \'%s\', name \'%s\', and status \'%s\' was '
                 'found.' % (content_item['id'], content_item['name'],
                             content_item['status']))
        content_statement.offset += dfp.SUGGESTED_PAGE_LIMIT
      else:
        break

    print '\nNumber of results found: %s' % response['totalResultSetSize']

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
