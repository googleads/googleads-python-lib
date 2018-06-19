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
"""This example gets all custom fields.
"""

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  custom_field_service = client.GetService(
      'CustomFieldService', version='v201802')

  # Create a statement to select custom fields.
  statement = dfp.StatementBuilder()

  # Retrieve a small amount of custom fields at a time, paging
  # through until all custom fields have been retrieved.
  while True:
    response = custom_field_service.getCustomFieldsByStatement(
        statement.ToStatement())
    if 'results' in response and len(response['results']):
      for custom_field in response['results']:
        # Print out some information for each custom field.
        print('Custom field with ID "%d" and name "%s" was found.\n' %
              (custom_field['id'], custom_field['name']))
      statement.offset += statement.limit
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
