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

"""This example gets all CmsMetadataKeys."""

# Import appropriate modules from the client library.
from __future__ import print_function
from googleads import ad_manager


def main(client):
  # Initialize appropriate service.
  cms_metadata_service = client.GetService(
      'CmsMetadataService', version='v202211')

  # Create a statement to select CmsMetadataKeys.
  statement = ad_manager.StatementBuilder(version='v202211')

  # Retrieve a small amount of keys at a time, paging
  # through until all keys have been retrieved.
  while True:
    response = cms_metadata_service.getCmsMetadataKeysByStatement(
        statement.ToStatement())
    if 'results' in response and len(response['results']):
      for cms_metadata_key in response['results']:
        # Print out some information for each key.
        print('CMS metadata key with Id %d and name "%s" was found.\n' %
              (cms_metadata_key['id'], cms_metadata_key['name']))
      statement.offset += statement.limit
    else:
      break

  print('\nNumber of results found: %s' % response['totalResultSetSize'])


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
