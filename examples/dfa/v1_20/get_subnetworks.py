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

"""Displays subnetwork names, IDs, and subnetwork IDs for a given search string.

Results are limited to 10.

Note that the permissions assigned to a subnetwork are not returned in a
human-readable format with this example. Run get_available_permissions.py to
see what permissions are available on a subnetwork.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import dfa


def main(client):
  # Initialize appropriate service.
  subnetwork_service = client.GetService(
      'subnetwork', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Set subnetwork search criteria.
  subnetwork_search_criteria = {
      'pageSize': '10'
  }

  # Get subnetworks.
  results = subnetwork_service.getSubnetworks(
      subnetwork_search_criteria)

  # Display subnetwork names, IDs, and subnetwork IDs.
  if results['records']:
    for subnetwork in results['records']:
      print ('Subnetwork with name \'%s\', ID \'%s\', part of network ID \'%s\''
             ' was found.' % (subnetwork['name'], subnetwork['id'],
                              subnetwork['networkId']))
  else:
    print 'No subnetworks found for your criteria.'


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client)
