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

"""This example creates a user role in a given DFA subnetwork.

To get the subnetwork ID, run get_subnetworks.py. To get the available
permissions, run get_available_permissions.py. To get the parent user role ID,
run get_user_roles.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: userrole.saveUserRole
"""

__author__ = 'Joseph DiLallo'

# Import appropriate modules from the client library.
from googleads import dfa


USER_ROLE_NAME = 'INSERT_USER_ROLE_NAME_HERE'
SUBNETWORK_ID = 'INSERT_SUBNETWORK_ID_HERE'
PARENT_USER_ROLE_ID = 'INSERT_PARENT_USER_ROLE_ID_HERE'
PERMISSION1_ID = 'INSERT_FIRST_PERMISSION_ID_HERE'
PERMISSION2_ID = 'INSERT_SECOND_PERMISSION_ID_HERE'


def main(client, user_role_name, subnetwork_id, parent_user_role_id,
         permission1_id, permission2_id):
  # Initialize appropriate service.
  user_role_service = client.GetService(
      'userrole', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Construct and the basic user role structure.
  user_role = {
      'name': user_role_name,
      'subnetworkId': subnetwork_id,
      'parentUserRoleId': parent_user_role_id
  }

  # Create an array of all permissions assigned to this user role and add it to
  # the user role structure. To get a list of available permissions, run
  # get_available_permissions.py.
  permission1 = {
      'id': permission1_id
  }
  permission2 = {
      'id': permission2_id
  }
  user_role['permissions'] = [permission1, permission2]

  # Save the user role.
  result = user_role_service.saveUserRole(user_role)

  # Display results.
  print 'User role with ID \'%s\' was created.' % result['id']


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client, USER_ROLE_NAME, SUBNETWORK_ID, PARENT_USER_ROLE_ID,
       PERMISSION1_ID, PERMISSION2_ID)
