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

"""This code example gets all roles.

This sample can be used to determine which role id is needed when getting and
creating users."""

__author__ = ('Nicholas Chen',
              'Joseph DiLallo')

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  user_service = client.GetService('UserService', version='v201505')

  # Get all roles.
  roles = user_service.getAllRoles()

  # Display results.
  for role in roles:
    print ('Role with id \'%s\' and name \'%s\' was found.'
           % (role['id'], role['name']))

  print '\nNumber of results found: %s' % len(roles)

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
