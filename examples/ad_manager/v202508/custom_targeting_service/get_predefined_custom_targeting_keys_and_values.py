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
"""This example gets all custom targeting keys and values.
"""

# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  # Initialize appropriate service.
  custom_targeting_service = client.GetService(
      'CustomTargetingService', version='v202508')

  # Create statement to get targeting keys for predefined values.
  targeting_key_statement = (ad_manager.StatementBuilder(version='v202508')
                             .Where('type = :type')
                             .WithBindVariable('type', 'PREDEFINED'))

  all_keys = []

  # Get custom targeting keys by statement.
  while True:
    response = custom_targeting_service.getCustomTargetingKeysByStatement(
        targeting_key_statement.ToStatement())
    if 'results' in response and len(response['results']):
      all_keys.extend(response['results'])
      targeting_key_statement.offset += targeting_key_statement.limit
    else:
      break

  if all_keys:
    # Create a statement to select custom targeting values.
    statement = (ad_manager.StatementBuilder(version='v202508')
                 .Where('customTargetingKeyId IN (:ids)')
                 .WithBindVariable('ids', [key['id'] for key in all_keys]))

    # Retrieve a small amount of custom targeting values at a time, paging
    # through until all custom targeting values have been retrieved.
    while True:
      response = custom_targeting_service.getCustomTargetingValuesByStatement(
          statement.ToStatement())
      if 'results' in response and len(response['results']):
        for custom_targeting_value in response['results']:
          # Print out some information for each custom targeting value.
          print('Custom targeting value with ID "%d", name "%s", display name '
                '"%s", and custom targeting key ID "%d" was found.\n' %
                (custom_targeting_value['id'], custom_targeting_value['name'],
                 custom_targeting_value['displayName'],
                 custom_targeting_value['customTargetingKeyId']))
        statement.offset += statement.limit
      else:
        break

    print('\nNumber of results found: %s' % response['totalResultSetSize'])


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
