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

"""This example gets all custom fields that apply to line items.

To create custom fields, run create_custom_fields.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: CustomFieldService.getCustomFieldsByStatement
"""

__author__ = ('Nicholas Chen',
              'Joseph DiLallo')

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  custom_field_service = client.GetService(
      'CustomFieldService', version='v201502')

  # Create statement to select only custom fields that apply to line items.
  values = [{
      'key': 'entityType',
      'value': {
          'xsi_type': 'TextValue',
          'value': 'LINE_ITEM'
      }
  }]
  query = 'WHERE entityType = :entityType'

  # Create a filter statement.
  statement = dfp.FilterStatement(query, values)

  # Get custom fields by statement.
  while True:
    response = custom_field_service.getCustomFieldsByStatement(
        statement.ToStatement())
    if 'results' in response:
      # Display results.
      for custom_field in response['results']:
        print ('Custom field with ID \'%s\' and name \'%s\' was found.'
               % (custom_field['id'], custom_field['name']))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
