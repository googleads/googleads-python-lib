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

"""Displays the permissions that a user role or subnetwork may be granted.

To get a subnetwork ID, run get_subnetworks.py.

A user role may not be set with more permissions than the subnetwork it
belongs to. You may enter a subnetwork ID to see the maximum permissions a
user role belonging to it can have, or enter '0' as the subnetwork ID to see
all possible permissions.

Tags: userrole.getAvailablePermissions
"""

__author__ = 'Joseph DiLallo'

# Import appropriate classes from the client library.
from googleads import dfa


SUBNETWORK_ID = 'INSERT_SUBNETWORK_ID_HERE'


def main(client, subnetwork_id):
  # Initialize appropriate service.
  user_role_service = client.GetService(
      'userrole', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Get available permissions.
  results = user_role_service.getAvailablePermissions(subnetwork_id)

  # Display permission name and its ID.
  if results:
    for permission in results:
      print ('Permission with name \'%s\' and ID \'%s\' was found.'
             % (permission['name'], permission['id']))
  else:
    print 'No permissions found.'


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client, SUBNETWORK_ID)
