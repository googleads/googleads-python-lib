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
"""This example gets all users.
"""

# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  # Initialize appropriate service.
  user_service = client.GetService('UserService', version='v202508')

  # Create a statement to select users.
  statement = ad_manager.StatementBuilder(version='v202508')

  # Retrieve a small amount of users at a time, paging
  # through until all users have been retrieved.
  while True:
    response = user_service.getUsersByStatement(statement.ToStatement())
    if 'results' in response and len(response['results']):
      for user in response['results']:
        # Print out some information for each user.
        print('User with ID "%d" and name "%s" was found.\n' % (user['id'],
                                                                user['name']))
      statement.offset += statement.limit
    else:
      break

  print('\nNumber of results found: %s' % response['totalResultSetSize'])


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
