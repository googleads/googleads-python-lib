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

"""This example adds a user to a team by creating an association between them.

To determine which teams exists, run get_all_teams.py. To determine which
users exist, run get_all_users.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import dfp

TEAM_ID = 'INSERT_TEAM_ID_HERE'
USER_IDS = ['INSERT_USER_IDS_TO_ASSOCIATE_TO_TEAM_HERE']


def main(client, team_id, user_ids):
  # Initialize appropriate service.
  user_team_association_service = client.GetService(
      'UserTeamAssociationService', version='v201608')

  user_team_associations = []
  for user_id in user_ids:
    user_team_associations.append(
        {
            'teamId': team_id,
            'userId': user_id
        })

  # Create the user team association on the server.
  user_team_associations = (
      user_team_association_service.createUserTeamAssociations(
          user_team_associations))

  # Display results.
  if user_team_associations:
    for user_team_association in user_team_associations:
      print ('A user team association between user with ID \'%s\' and team with'
             ' ID \'%s\'was created.' % (user_team_association['userId'],
                                         user_team_association['teamId']))
  else:
    print 'No user team associations created.'

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, TEAM_ID, USER_IDS)
