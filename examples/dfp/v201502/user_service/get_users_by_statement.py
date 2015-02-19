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

"""This code example gets a user by its id.

To create users, run create_user.py."""

__author__ = ('Nicholas Chen',
              'Joseph DiLallo')

# Import appropriate modules from the client library.
from googleads import dfp

USER_ID = 'INSERT_USER_ID_TO_FIND_HERE'


def main(client, user_id):
  # Initialize appropriate service.
  user_service = client.GetService('UserService', version='v201502')

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
  users = response['results'] if 'results' in response else []

  for user in users:
    # Display results.
    print ('User with id \'%s\', email \'%s\', and role \'%s\' was found.'
           % (user['id'], user['email'], user['roleName']))

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, USER_ID)
