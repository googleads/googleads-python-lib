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

"""This code example updates content metadata key hierarchies.

To determine which content metadata key hierarchies exist, run
get_all_content_metadata_key_hierarchies.py.

This feature is only available to DFP video publishers.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: ContentMetadataKeyHierarchyService.getContentMetadataKeyHierarchiesByStatement
      ContentMetadataKeyHierarchyService.updateContentMetadataKeyHierarchies
"""

__author__ = ('Nicholas Chen',
              'Joseph DiLallo')

# Import appropriate modules from the client library.
from googleads import dfp

# Set the ID of the content metadata key hierarchy to update.
CONTENT_METADATA_KEY_HIERARCHY_ID = (
    'INSERT_CONTENT_METADATA_KEY_HIERARCHY_ID_HERE')
# Set the ID of the custom targeting key to be added as a hierarchy level.
CUSTOM_TARGETING_KEY_ID = 'INSERT_CUSTOM_TARGETING_KEY_ID_HERE'


def main(client, content_metadata_key_hierarchy_id, custom_targeting_key_id):
  # Initialize appropriate service.
  content_metadata_key_hierarchy_service = client.GetService(
      'ContentMetadataKeyHierarchyService', version='v201405')

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
                  statement.ToStatement()))[0]
  content_metadata_key_hierarchies = (response['results']
                                      if 'results' in response else None)

  if content_metadata_key_hierarchies:
    content_metadata_key_hierarchy = content_metadata_key_hierarchies[0]

    # Update the content metadata key hierarchy by adding a hierarchy level.
    hierarchy_levels = content_metadata_key_hierarchy['hierarchyLevels']

    hierarchy_level = {
        'customTargetingKeyId': custom_targeting_key_id,
        'hierarchyLevel': str(len(hierarchy_levels) + 1)
    }

    content_metadata_key_hierarchy['hierarchyLevels'] = (
        hierarchy_levels.append(hierarchy_level))

    content_metadata_key_hierarchies = (
        content_metadata_key_hierarchy_service
        .updateContentMetadataKeyHierarchies(content_metadata_key_hierarchies))

    # Display results.
    for content_metadata_key_hierarchy in content_metadata_key_hierarchies:
      print ('Content metadata key hierarchy with id \'%s\' and name \'%s\''
             ' was updated.' % (content_metadata_key_hierarchy['id'],
                                content_metadata_key_hierarchy['name']))

  else:
    print 'No content metadata key hierarchies were found'

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, CONTENT_METADATA_KEY_HIERARCHY_ID, CUSTOM_TARGETING_KEY_ID)
