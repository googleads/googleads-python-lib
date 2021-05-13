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
"""This example gets all user team associations (i.e. teams) for a given user.
"""

# Import appropriate modules from the client library.
from googleads import ad_manager

USER_ID = 'INSERT_USER_ID_HERE'


def main(client, user_id):
  # Initialize appropriate service.
  user_team_association_service = client.GetService(
      'UserTeamAssociationService', version='v202105')
  # Create a statement to select user team associations.
  statement = (ad_manager.StatementBuilder(version='v202105')
               .Where('userId = :userId')
               .WithBindVariable('userId', int(user_id)))

  # Retrieve a small amount of user team associations at a time, paging
  # through until all user team associations have been retrieved.
  while True:
    response = user_team_association_service.getUserTeamAssociationsByStatement(
        statement.ToStatement())
    if 'results' in response and len(response['results']):
      for user_team_association in response['results']:
        # Print out some information for each user team association.
        print('User team association with user ID "%d" and team ID "%d" was '
              'found.\n' % (user_team_association['userId'],
                            user_team_association['teamId']))
      statement.offset += statement.limit
    else:
      break

  print('\nNumber of results found: %s' % response['totalResultSetSize'])


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, USER_ID)
