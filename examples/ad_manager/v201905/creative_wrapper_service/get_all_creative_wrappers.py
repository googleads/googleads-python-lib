#!/usr/bin/env python
#
# Copyright 2016 Google Inc. All Rights Reserved.
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
"""This example gets all creative wrappers.
"""

# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  # Initialize appropriate service.
  creative_wrapper_service = client.GetService(
      'CreativeWrapperService', version='v201905')

  # Create a statement to select creative wrappers.
  statement = ad_manager.StatementBuilder(version='v201905')

  # Retrieve a small amount of creative wrappers at a time, paging
  # through until all creative wrappers have been retrieved.
  while True:
    response = creative_wrapper_service.getCreativeWrappersByStatement(
        statement.ToStatement())
    if 'results' in response and len(response['results']):
      for creative_wrapper in response['results']:
        # Print out some information for each creative wrapper.
        print('Creative wrapper with ID "%d" and label id "%d" was found.\n' %
              (creative_wrapper['id'], creative_wrapper['labelId']))
      statement.offset += statement.limit
    else:
      break

  print('\nNumber of results found: %s' % response['totalResultSetSize'])


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
