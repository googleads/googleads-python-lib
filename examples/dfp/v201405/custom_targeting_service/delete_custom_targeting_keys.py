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

"""This example deletes a custom targeting key by its name.

To determine which custom targeting keys exist, run
get_all_custom_targeting_keys_and_values.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: CustomTargetingService.getCustomTargetingKeysByStatement
"""

__author__ = ('Nicholas Chen',
              'Joseph DiLallo')

# Import appropriate modules from the client library.
from googleads import dfp

KEY_NAME = 'INSERT_CUSTOM_TARGETING_KEY_NAME_HERE'


def main(client, key_name):
  # Initialize appropriate service.
  custom_targeting_service = client.GetService(
      'CustomTargetingService', version='v201405')

  values = [{
      'key': 'name',
      'value': {
          'xsi_type': 'TextValue',
          'value': key_name
      }
  }]
  query = 'WHERE name = :name'
  statement = dfp.FilterStatement(query, values)

  deleted_custom_targeting_keys = 0

  # Get custom targeting keys.
  while True:
    response = custom_targeting_service.getCustomTargetingKeysByStatement(
        statement.ToStatement())
    if 'results' in response:
      key_ids = [key['id'] for key in response['results']]
      action = {'xsi_type': 'DeleteCustomTargetingKeys'}
      key_query = 'WHERE id IN (%s)' % ', '.join(key_ids)
      key_statement = dfp.FilterStatement(key_query)

      # Delete custom targeting keys.
      result = custom_targeting_service.performCustomTargetingKeyAction(
          action, key_statement.ToStatement())

      if result and int(result['numChanges']) > 0:
        deleted_custom_targeting_keys += int(result['numChanges'])
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  if deleted_custom_targeting_keys > 0:
    print ('Number of custom targeting keys deleted: %s'
           % deleted_custom_targeting_keys)
  else:
    print 'No custom targeting keys were deleted.'

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, KEY_NAME)
