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

"""This code example gets all content metadata key hierarchies.

This feature is only available to DFP video publishers.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  content_metadata_key_hierarchy_service = client.GetService(
      'ContentMetadataKeyHierarchyService', version='v201502')

  # Create statement object to select all content.
  statement = dfp.FilterStatement()

  # Get content by statement.
  while True:
    response = (content_metadata_key_hierarchy_service
                .getContentMetadataKeyHierarchiesByStatement(
                    statement.ToStatement())[0])
    content_metadata_key_hierarchies = (response['results']
                                        if 'results' in response else None)
    if content_metadata_key_hierarchies:
      # Display results.
      for content_metadata_key_hierarchy in content_metadata_key_hierarchies:
        print ('Content metadata key hierarchyy with id \'%s\' and name \'%s\''
               ' was found.' % (content_metadata_key_hierarchy['id'],
                                content_metadata_key_hierarchy['name']))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
