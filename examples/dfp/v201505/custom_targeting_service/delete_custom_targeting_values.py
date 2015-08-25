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

"""This example deletes custom targeting values for a given custom targeting
key.

To determine which custom targeting keys and values exist, run
get_all_custom_targeting_keys_and_values.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import dfp

KEY_ID = 'INSERT_CUSTOM_TARGETING_KEY_ID_HERE'


def main(client, key_id):
  # Initialize appropriate service.
  custom_targeting_service = client.GetService(
      'CustomTargetingService', version='v201505')

  filter_values = [{
      'key': 'keyId',
      'value': {
          'xsi_type': 'NumberValue',
          'value': key_id
      }
  }]
  query = 'WHERE customTargetingKeyId = :keyId'
  statement = dfp.FilterStatement(query, filter_values)

  deleted_custom_targeting_values = 0

  # Get custom targeting values.
  while True:
    response = custom_targeting_service.getCustomTargetingValuesByStatement(
        statement.ToStatement())
    if 'results' in response:
      value_ids = [value['id'] for value in response['results']]
      action = {'xsi_type': 'DeleteCustomTargetingValues'}
      value_query = ('WHERE customTargetingKeyId = :keyId '
                     'AND id IN (%s)' % ', '.join(value_ids))
      value_statement = dfp.FilterStatement(value_query, filter_values)

      # Delete custom targeting values.
      result = custom_targeting_service.performCustomTargetingValueAction(
          action, value_statement.ToStatement())
      if result and int(result['numChanges']) > 0:
        deleted_custom_targeting_values += int(result['numChanges'])
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  if deleted_custom_targeting_values > 0:
    print ('Number of custom targeting values deleted: %s'
           % deleted_custom_targeting_values)
  else:
    print 'No custom targeting values were deleted.'

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, KEY_ID)
