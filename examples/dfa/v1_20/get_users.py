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

"""This example displays users for the given search criteria.

Results are limited to the first 10 records.

Tags: user.getUsersByCriteria
"""

__author__ = 'Joseph DiLallo'

# Import appropriate modules from the client library.
from googleads import dfa


def main(client):
  # Initialize appropriate service.
  user_service = client.GetService(
      'user', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Set user search criteria.
  user_search_criteria = {
      'pageSize': '10'
  }

  # Get users that match the search criteria.
  results = user_service.getUsersByCriteria(user_search_criteria)

  # Display user names, IDs, network IDs, subnetwork IDs, and group IDs.
  if results['records']:
    for user in results['records']:
      print ('User with name \'%s\', ID \'%s\', network ID \'%s\', '
             'subnetwork ID \'%s\', and user role id \'%s\' was found.'
             % (user['name'], user['id'], user['networkId'],
                user['subnetworkId'], user['userGroupId']))
  else:
    print 'No users found for your criteria.'


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client)
