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

"""This example creates custom field options for a drop-down custom field.

Once created, custom field options can be found under the options fields of the
drop-down custom field and they cannot be deleted. To determine which custom
fields exist, run get_all_custom_fields.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: CustomFieldService.createCustomFieldOptions
"""

__author__ = ('Nicholas Chen',
              'Joseph DiLallo')

# Import appropriate modules from the client library.
from googleads import dfp

# Set the ID of the drop-down custom field to create options for.
CUSTOM_FIELD_ID = 'INSERT_DROP_DOWN_CUSTOM_FIELD_ID_HERE'


def main(client, custom_field_id):
  # Initialize appropriate service.
  custom_field_service = client.GetService(
      'CustomFieldService', version='v201502')

  # Create custom field options.
  custom_field_options = [
      {
          'displayName': 'Approved',
          'customFieldId': custom_field_id
      },
      {
          'displayName': 'Unapproved',
          'customFieldId': custom_field_id
      }
  ]

  # Add custom field options.
  custom_field_options = custom_field_service.createCustomFieldOptions(
      custom_field_options)

  # Display results.
  for custom_field_option in custom_field_options:
    print ('Custom field option with ID \'%s\' and name \'%s\' was created.'
           % (custom_field_option['id'], custom_field_option['displayName']))

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, CUSTOM_FIELD_ID)
