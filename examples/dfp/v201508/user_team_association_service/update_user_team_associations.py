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

"""This example updates user team associations.

It updates a user team association by setting the overridden access type to read
only for all teams that the user belongs to. To determine which users exists,
run get_all_users.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import dfp

USER_ID = 'INSERT_USER_ID_TO_UPDATE_HERE'


def main(client, user_id):
  # Initialize appropriate service.
  user_team_association_service = client.GetService(
      'UserTeamAssociationService', version='v201508')

  # Create filter text to select user team associations by the user ID.
  values = [{
      'key': 'userId',
      'value': {
          'xsi_type': 'NumberValue',
          'value': user_id
      }
  }]
  query = 'WHERE userId = :userId'

  # Create a filter statement.
  statement = dfp.FilterStatement(query, values)

  # Get user team associations by statement.
  response = user_team_association_service.getUserTeamAssociationsByStatement(
      statement.ToStatement())

  if 'results' in response:
    updated_user_team_associations = []
    # Update each local user team association to read only access.
    for user_team_association in response['results']:
      user_team_association['overriddenTeamAccessType'] = 'READ_ONLY'
      updated_user_team_associations.append(user_team_association)

    # Update user team associations on the server.
    user_team_associations = (
        user_team_association_service.updateUserTeamAssociations(
            updated_user_team_associations))

    # Display results.
    if user_team_associations:
      for user_team_association in user_team_associations:
        print ('User team association between user with ID \'%s\' and team with'
               ' ID \'%s\' was updated.' % (user_team_association['userId'],
                                            user_team_association['teamId']))
    else:
      print 'No user team associations were updated.'
  else:
    print 'No user team associations found to update.'

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, USER_ID)
