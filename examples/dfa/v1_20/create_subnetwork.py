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

"""This example creates a subnetwork in a given DFA network.

To get the network ID, run get_users.py. To get the available permissions, run
get_available_permissions.py.

Tags: subnetwork.saveSubnetwork
"""

__author__ = 'Joseph DiLallo'

# Import appropriate classes from the client library.
from googleads import dfa


NETWORK_ID = 'INSERT_NETWORK_ID_HERE'
SUBNETWORK_NAME = 'INSERT_SUBNETWORK_NAME_HERE'
PERMISSION1 = 'INSERT_FIRST_PERMISSION_ID_HERE'
PERMISSION2 = 'INSERT_SECOND_PERMISSION_ID_HERE'


def main(client, network_id, subnetwork_name, permission1, permission2):
  # Initialize appropriate service.
  subnetwork_service = client.GetService(
      'subnetwork', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Construct and the basic subnetwork structure.
  subnetwork = {
      'name': subnetwork_name,
      'networkId': network_id
  }

  # Create an array of all permissions assigned to this subnetwork and add it to
  # the subnetwork structure. To get a list of available permissions, run
  # get_available_permissions.py.
  subnetwork['availablePermissions'] = [permission1, permission2]

  # Save the subnetwork.
  result = subnetwork_service.saveSubnetwork(subnetwork)

  # Display results.
  print 'Subnetwork with ID \'%s\' was created.' % result['id']


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client, NETWORK_ID, SUBNETWORK_NAME, PERMISSION1, PERMISSION2)
