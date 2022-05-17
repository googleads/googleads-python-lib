#!/usr/bin/env python
#
# Copyright 2019 Google LLC
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

"""This example gets all CmsMetadataValues for a particular CmsMetadataKey."""

# Import appropriate modules from the client library.
from __future__ import print_function
from googleads import ad_manager

CMS_METADATA_KEY_NAME = 'INSERT_CMS_METADATA_KEY_NAME_HERE'


def main(client, cms_metadata_key_name):
  # Initialize appropriate service.
  cms_metadata_service = client.GetService(
      'CmsMetadataService', version='v202205')

  # Create a statement to select CmsMetadataValues for a particular key.
  statement = (
      ad_manager.StatementBuilder(version='v202205').Where(
          'cmsKey = :cmsMetadataKeyName').WithBindVariable(
              'cmsMetadataKeyName', cms_metadata_key_name))

  # Retrieve a small amount of values at a time, paging
  # through until all values have been retrieved.
  while True:
    response = cms_metadata_service.getCmsMetadataValuesByStatement(
        statement.ToStatement())
    if 'results' in response and len(response['results']):
      for cms_metadata_value in response['results']:
        # Print out some information for each value.
        print(('CMS metadata value with Id %d and name "%s", associated with '
               'the CmsMetadataKey with id %d and name "%s", was found.\n') %
              (cms_metadata_value['cmsMetadataValueId'],
               cms_metadata_value['valueName'], cms_metadata_value['key']['id'],
               cms_metadata_value['key']['name']))
      statement.offset += statement.limit
    else:
      break

  print('\nNumber of results found: %s' % response['totalResultSetSize'])


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, CMS_METADATA_KEY_NAME)
