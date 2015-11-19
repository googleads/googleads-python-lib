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

"""This example creates custom fields.

To determine which custom fields exist, run get_all_custom_fields.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


import uuid

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  custom_field_service = client.GetService(
      'CustomFieldService', version='v201511')

  # Create custom field objects.
  custom_fields = [
      {
          'name': 'Customer comments #%s' % uuid.uuid4(),
          'entityType': 'LINE_ITEM',
          'dataType': 'STRING',
          'visibility': 'FULL'
      }, {
          'name': 'Internal approval status #%s' % uuid.uuid4(),
          'entityType': 'LINE_ITEM',
          'dataType': 'DROP_DOWN',
          'visibility': 'FULL'
      }
  ]

  # Add custom fields.
  custom_fields = custom_field_service.createCustomFields(custom_fields)

  # Display results.
  for custom_field in custom_fields:
    print ('Custom field with ID \'%s\' and name \'%s\' was created.'
           % (custom_field['id'], custom_field['name']))

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
