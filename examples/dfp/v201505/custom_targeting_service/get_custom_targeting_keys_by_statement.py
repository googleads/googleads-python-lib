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

"""This example gets all predefined custom targeting keys.

To create custom targeting keys, run create_custom_targeting_keys_and_values.py.
"""


# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  custom_targeting_service = client.GetService(
      'CustomTargetingService', version='v201505')

  values = [{
      'key': 'type',
      'value': {
          'xsi_type': 'TextValue',
          'value': 'PREDEFINED'
      }
  }]
  query = 'WHERE type = :type'
  statement = dfp.FilterStatement(query, values)

  # Get custom targeting keys by statement.
  while True:
    response = custom_targeting_service.getCustomTargetingKeysByStatement(
        statement.ToStatement())
    if 'results' in response:
      # Display results.
      for key in response['results']:
        print ('Custom targeting key with id \'%s\', name \'%s\', display name '
               '\'%s\', and type \'%s\' was found.'
               % (key['id'], key['name'], key['displayName'], key['type']))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
