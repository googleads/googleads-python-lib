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

"""This example updates the display name of a single custom targeting key.

To determine which custom targeting keys exist, run
get_all_custom_targeting_keys_and_values.py."""

__author__ = ('Nicholas Chen',
              'Joseph DiLallo')

# Import appropriate modules from the client library.
from googleads import dfp

CUSTOM_TARGETING_KEY_ID = 'INSERT_CUSTOM_TARGETING_KEY_ID_HERE'


def main(client, key_id):
  # Initialize appropriate service.
  custom_targeting_service = client.GetService(
      'CustomTargetingService', version='v201408')

  values = [{
      'key': 'keyId',
      'value': {
          'xsi_type': 'NumberValue',
          'value': key_id
      }
  }]
  query = 'WHERE id = :keyId'
  statement = dfp.FilterStatement(query, values, 1)

  # Get custom targeting keys by statement.
  response = custom_targeting_service.getCustomTargetingKeysByStatement(
      statement.ToStatement())

  # Update each local custom targeting key object by changing its display name.
  if 'results' in response:
    updated_keys = []
    for key in response['results']:
      if not key['displayName']:
        key['displayName'] = key['name']
      key['displayName'] += ' (Deprecated)'
      updated_keys.append(key)
    keys = custom_targeting_service.updateCustomTargetingKeys(updated_keys)

    # Display results.
    if keys:
      for key in keys:
        print ('Custom targeting key with id \'%s\', name \'%s\', display name '
               '\'%s\', and type \'%s\' was updated.'
               % (key['id'], key['name'], key['displayName'], key['type']))
  else:
    print 'No custom targeting keys were found to update.'

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, CUSTOM_TARGETING_KEY_ID)
