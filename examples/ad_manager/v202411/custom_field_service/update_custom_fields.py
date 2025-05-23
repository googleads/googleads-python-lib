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

"""This example updates custom field descriptions.

To determine which custom fields exist, run get_all_custom_fields.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import ad_manager

# Set the ID of the custom field to update.
CUSTOM_FIELD_ID = 'INSERT_CUSTOM_FIELD_ID_HERE'


def main(client, custom_field_id):
  # Initialize appropriate service.
  custom_field_service = client.GetService(
      'CustomFieldService', version='v202411')

  # Create statement to get a custom field.
  statement = (ad_manager.StatementBuilder(version='v202411')
               .Where('id = :customFieldId')
               .WithBindVariable('customFieldId', int(custom_field_id)))

  # Get custom field.
  custom_fields = custom_field_service.getCustomsFieldByStatement(
      statement.ToStatement())

  if custom_fields:
    for custom_field in custom_fields:
      custom_field['description'] += ' Updated.'

    # Update the custom field on the server.
    custom_fields = custom_field_service.updateCustomFields(custom_fields)

    # Display results.
    for custom_field in custom_fields:
      print(('Custom field with ID "%s", name "%s", and '
             'description "%s" was updated.')
            % (custom_field['id'], custom_field['name'],
                custom_field['description']))
  else:
    print('No custom fields found to update.')


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, CUSTOM_FIELD_ID)
