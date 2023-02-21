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

"""This code example creates new users.

To determine which users exist, run get_all_users.py.
"""


# Import appropriate modules from the client library.
from googleads import ad_manager

NEW_USER_EMAIL_ADDRESS = 'INSERT_EMAIL_ADDRESS_HERE'
NEW_USER_NAME = 'INSERT_NAME_HERE'


def main(client, email, name):
  # Initialize appropriate service.
  user_service = client.GetService('UserService', version='v202302')

  # Create user objects.
  users = [
      {
          'email': email,
          'name': name,
      }
  ]
  for user in users:
    # Set the system defined ID of the trafficker role.
    # To determine what other roles exist, run get_all_roles.py.
    user['roleId'] = '-7'

  # Add users.
  users = user_service.createUsers(users)

  # Display results.
  for user in users:
    print('User with id "%s", email "%s", and role "%s" was created.'
          % (user['id'], user['email'], user['roleName']))

if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, NEW_USER_EMAIL_ADDRESS, NEW_USER_NAME)
