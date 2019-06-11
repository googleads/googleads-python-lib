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

"""This example removes the user from all its teams.

To determine which users exist, run get_all_users.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import ad_manager

USER_ID = 'INSERT_USER_ID_HERE'


def main(client, user_id):
  # Initialize appropriate service.
  user_team_association_service = client.GetService(
      'UserTeamAssociationService', version='v201811')

  # Create filter text to select user team associations by the user ID.
  statement = (ad_manager.StatementBuilder(version='v201811')
               .Where('userId = :userId')
               .WithBindVariable('userId', int(user_id)))

  # Get user team associations by statement.
  response = user_team_association_service.getUserTeamAssociationsByStatement(
      statement.ToStatement())
  user_team_associations = response['results'] if 'results' in response else []

  for user_team_association in user_team_associations:
    print('User team association between user with ID "%s" and team with '
          'ID "%s" will be deleted.' % (user_team_association['userId'],
                                        user_team_association['teamId']))
  print('Number of teams that the user will be removed from: %s' %
        len(user_team_associations))

  # Action doesn't require limit/offset
  statement.limit = None
  statement.offset = None

  # Perform action.
  result = user_team_association_service.performUserTeamAssociationAction(
      {'xsi_type': 'DeleteUserTeamAssociations'},
      statement.ToStatement())

  # Display results.
  if result and int(result['numChanges']) > 0:
    print('Number of teams that the user was removed from: %s'
          % result['numChanges'])
  else:
    print('No user team associations were deleted.')


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, USER_ID)
