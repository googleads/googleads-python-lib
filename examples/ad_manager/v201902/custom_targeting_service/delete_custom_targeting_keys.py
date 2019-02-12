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

"""This example deletes a custom targeting key by its name.

To determine which custom targeting keys exist, run
get_all_custom_targeting_keys_and_values.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import ad_manager

KEY_NAME = 'INSERT_CUSTOM_TARGETING_KEY_NAME_HERE'


def main(client, key_name):
  # Initialize appropriate service.
  custom_targeting_service = client.GetService(
      'CustomTargetingService', version='v201902')

  statement = (ad_manager.StatementBuilder(version='v201902')
               .Where('name = :name')
               .WithBindVariable('name', key_name))

  deleted_custom_targeting_keys = 0

  # Get custom targeting keys.
  while True:
    response = custom_targeting_service.getCustomTargetingKeysByStatement(
        statement.ToStatement())
    if 'results' in response and len(response['results']):
      key_ids = [str(key['id']) for key in response['results']]
      action = {'xsi_type': 'DeleteCustomTargetingKeys'}
      key_statement = (ad_manager.StatementBuilder(version='v201902')
                       .Where('id IN (%s)' % ', '.join(key_ids)))

      # Delete custom targeting keys.
      result = custom_targeting_service.performCustomTargetingKeyAction(
          action, key_statement.ToStatement())

      if result and int(result['numChanges']) > 0:
        deleted_custom_targeting_keys += int(result['numChanges'])
      statement.offset += statement.limit
    else:
      break

  if deleted_custom_targeting_keys > 0:
    print ('Number of custom targeting keys deleted: %s'
           % deleted_custom_targeting_keys)
  else:
    print 'No custom targeting keys were deleted.'


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, KEY_NAME)
