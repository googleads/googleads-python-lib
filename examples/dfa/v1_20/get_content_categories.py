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

"""This example displays available content categories for a given search string.

Results are limited to 10.

Tags: contentcategory.getContentCategories
"""

__author__ = 'Joseph DiLallo'

# Import appropriate modules from the client library.
from googleads import dfa


def main(client):
  # Initialize appropriate service.
  content_category_service = client.GetService(
      'contentcategory', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Create content category search criteria structure.
  content_category_search_criteria = {
      'pageSize': '10'
  }

  # Get content category record set.
  results = content_category_service.getContentCategories(
      content_category_search_criteria)

  # Display content category names, IDs and descriptions.
  if results['records']:
    for content_category in results['records']:
      print ('Content category with name \'%s\' and ID \'%s\' was found.'
             % (content_category['name'], content_category['id']))
  else:
    print 'No content categories found for your criteria.'


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client)
