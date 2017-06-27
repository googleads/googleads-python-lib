#!/usr/bin/env python
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

"""This code example deletes content metadata key hierarchies.

To determine which content metadata key hierarchies exist, run
get_all_content_metadata_key_hierarchies.py.

This feature is only available to DFP video publishers.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import dfp

# Set the ID of the content metadata key hierarchy to delete.
CONTENT_METADATA_KEY_HIERARCHY_ID = (
    'INSERT_CONTENT_METADATA_KEY_HIERARCHY_ID_HERE')


def main(client, content_metadata_key_hierarchy_id):
  # Initialize appropriate service.
  content_metadata_key_hierarchy_service = client.GetService(
      'ContentMetadataKeyHierarchyService', version='v201705')

  # Create a query to select a single content metadata key hierarchy.
  values = [{
      'key': 'id',
      'value': {
          'xsi_type': 'NumberValue',
          'value': content_metadata_key_hierarchy_id
      }
  }]

  query = 'WHERE id = :id ORDER BY id ASC'
  statement = dfp.FilterStatement(query, values, 1)

  # Get a single content metadata key hierarchy by statement.
  response = (content_metadata_key_hierarchy_service
              .getContentMetadataKeyHierarchiesByStatement(
                  statement.ToStatement())[0])
  content_metadata_key_hierarchies = (response['results']
                                      if 'results' in response else None)

  # Display results.
  if content_metadata_key_hierarchies:
    for content_metadata_key_hierarchy in content_metadata_key_hierarchies:
      print ('Content metadata key hierarchy with ID "%s" and name "%s" '
             'will be deleted.' % (content_metadata_key_hierarchy['id'],
                                   content_metadata_key_hierarchy['name']))

    # Perform action.
    result = (content_metadata_key_hierarchy_service
              .performContentMetadataKeyHierarchyAction(
                  {'type': 'DeleteContentMetadataKeyHierarchies'},
                  statement.ToStatement()))[0]

    # Display results.
    print ('Number of content metadata key hierarchies deleted: %s' %
           result['numChanges'])

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, CONTENT_METADATA_KEY_HIERARCHY_ID)
