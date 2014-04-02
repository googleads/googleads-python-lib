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

"""Displays user roles for the given search criteria.

Results are limited to the first 10 records.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: userrole.getUserRoles
"""

__author__ = 'Joseph DiLallo'

# Import appropriate modules from the client library.
from googleads import dfa


def main(client):
  # Initialize appropriate service.
  user_role_service = client.GetService(
      'userrole', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Set user role search criteria.
  user_role_search_criteria = {
      'pageSize': '10'
  }

  # Get user roles that match the search criteria.
  results = user_role_service.getUserRoles(user_role_search_criteria)

  # Display user role names, IDs, subnetwork IDs, number of assigned users, and
  # assigned permissions.
  if results['userRoles']:
    for user_role in results['userRoles']:
      print ('User role with name \'%s\', ID \'%s\', subnetwork ID \'%s\', and '
             'assigned to \'%s\' users was found.'
             % (user_role['name'], user_role['id'], user_role['subnetworkId'],
                user_role['totalAssignedUsers']))
      if user_role['permissions']:
        print '    The above user role has the following permissions:'
        for permission in user_role['permissions']:
          print ('        Permission with name \'%s\' and ID \'%s\'.'
                 % (permission['name'], permission['id']))
      else:
        print '    The above user role has no permissions assigned.'
  else:
    print 'No user roles found for your criteria.'


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client)
