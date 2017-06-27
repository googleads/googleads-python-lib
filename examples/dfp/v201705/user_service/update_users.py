#!/usr/bin/env python
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

"""This code example updates a user by adding " Sr." to the end of their name.

To determine which users exist, run get_all_users.py.
"""


# Import appropriate modules from the client library.
from googleads import dfp

USER_ID = 'INSERT_USER_ID_TO_UPDATE_HERE'


def main(client, user_id):
  # Initialize appropriate service.
  user_service = client.GetService('UserService', version='v201705')

  # Create query.
  values = [{
      'key': 'userId',
      'value': {
          'xsi_type': 'NumberValue',
          'value': user_id
      }
  }]
  query = 'WHERE id = :userId'

  # Create a filter statement.
  statement = dfp.FilterStatement(query, values)

  # Get users by statement.
  response = user_service.getUsersByStatement(statement.ToStatement())

  if 'results' in response:
    users = response['results']
    for user in users:
      user['name'] += ' Sr.'

    # Update users on server.
    users = user_service.updateUsers(users)
    for user in users:
      print ('User with id "%s" and name "%s" was updated.'
             % (user['id'], user['name']))
  else:
    print 'No users found to update.'

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, USER_ID)
