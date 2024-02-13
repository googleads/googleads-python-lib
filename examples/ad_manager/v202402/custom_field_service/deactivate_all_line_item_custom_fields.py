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

"""This example deactivates all active line items custom fields.

To determine which custom fields exist, run get_all_custom_fields.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  # Initialize appropriate service.
  custom_field_service = client.GetService(
      'CustomFieldService', version='v202402')

  # Create statement to select only active custom fields that apply to
  # line items.
  statement = (ad_manager.StatementBuilder(version='v202402')
               .Where('entityType = :entityType and isActive = :isActive')
               .WithBindVariable('entityType', 'LINE_ITEM')
               .WithBindVariable('isActive', True))

  custom_fields_deactivated = 0

  # Get custom fields by statement.
  while True:
    response = custom_field_service.getCustomFieldsByStatement(
        statement.ToStatement())
    if 'results' in response and len(response['results']):
      # Display results.
      for custom_field in response['results']:
        print('Custom field with ID "%s" and name "%s" will'
              ' be deactivated.' % (custom_field['id'], custom_field['name']))
        result = custom_field_service.performCustomFieldAction(
            {'xsi_type': 'DeactivateCustomFields'}, statement.ToStatement())
        if result and int(result['numChanges']) > 0:
          custom_fields_deactivated += int(result['numChanges'])
      statement.offset += statement.limit
    else:
      break

  if custom_fields_deactivated > 0:
    print('Number of custom fields deactivated: %s' % custom_fields_deactivated)
  else:
    print('No custom fields were deactivated.')


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
