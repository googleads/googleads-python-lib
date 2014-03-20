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

"""This code example gets all active activity groups.

To create activity groups, run create_activity_groups.py.

Tags: ActivityGroupService.getActivityGroupsByStatement
"""

__author__ = ('Nicholas Chen',
              'Joseph DiLallo')

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  activity_group_service = client.GetService('ActivityGroupService',
                                             version='v201403')

  # Create statement object to only select active activity groups.
  values = [{
      'key': 'status',
      'value': {
          'xsi_type': 'TextValue',
          'value': 'ACTIVE'
      }
  }]
  query = 'WHERE status = :status'

  # Create a filter statement.
  statement = dfp.FilterStatement(query, values)

  # Get activity groups by statement.
  while True:
    response = activity_group_service.getActivityGroupsByStatement(
        statement.ToStatement())
    if 'results' in response:
      # Display results.
      for activity_group in response['results']:
        print ('Activity group with ID \'%s\' and name \'%s\' was found.'
               % (activity_group['id'], activity_group['name']))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
