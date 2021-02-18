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

"""This example updates teams by changing its description.

To determine which teams exist, run get_all_teams.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import ad_manager

TEAM_ID = 'INSERT_TEAM_ID_HERE'


def main(client, team_id):
  # Initialize appropriate service.
  team_service = client.GetService('TeamService', version='v202102')

  # Create a filter statement to select a single team by ID.
  statement = (ad_manager.StatementBuilder(version='v202102')
               .Where('id = :teamId')
               .WithBindVariable('teamId', int(team_id)))

  # Get teams by statement.
  response = team_service.getTeamsByStatement(statement.ToStatement())

  if 'results' in response and len(response['results']):
    updated_teams = []
    # Update each local team object by changing its description.
    for team in response['results']:
      team['description'] = 'this team is great!'
      updated_teams.append(team)

    # Update teams on the server.
    teams = team_service.updateTeams(updated_teams)

    # Display results.
    for team in teams:
      print('Team with id "%s" and name "%s" was updated.'
            % (team['id'], team['name']))
  else:
    print('No teams found to update.')


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, TEAM_ID)
