#!/usr/bin/python
#
# Copyright 2014 Google Inc. All Rights Reserved.
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

"""This example updates teams by adding an ad unit to a team.

To determine which teams exist, run get_all_teams.py. To determine which ad
units exist, run get_all_ad_units.py

Tags: TeamService.getTeamsByStatement, TeamService.updateTeams
"""

__author__ = ('Nicholas Chen',
              'Joseph DiLallo')

# Import appropriate modules from the client library.
from googleads import dfp

AD_UNIT_ID = 'INSERT_AD_UNIT_ID_HERE'
TEAM_ID = 'INSERT_TEAM_ID_HERE'


def main(client, ad_unit_id, team_id):
  # Initialize appropriate service.
  team_service = client.GetService('TeamService', version='v201403')

  # Create a filter statement to select a single team by ID.
  values = [{
      'key': 'teamId',
      'value': {
          'xsi_type': 'NumberValue',
          'value': team_id
      }
  }]
  query = 'WHERE id = :teamId'
  statement = dfp.FilterStatement(query, values)

  # Get teams by statement.
  response = team_service.getTeamsByStatement(statement.ToStatement())

  if 'results' in response:
    updated_teams = []
    # Update each local team object by adding the ad unit to it.
    for team in response['results']:
      ad_unit_ids = []
      if 'adUnitIds' in team:
        ad_unit_ids = team['adUnitIds']
      # Don't add the ad unit if the team has all inventory already.
      if not team['hasAllInventory']:
        ad_unit_ids.append(ad_unit_id)
      team['adUnitIds'] = ad_unit_ids
      updated_teams.append(team)

    # Update teams on the server.
    teams = team_service.updateTeams(updated_teams)

    # Display results.
    for team in teams:
      print ('Team with id \'%s\' and name \'%s\' was updated.'
             % (team['id'], team['name']))
  else:
    print 'No teams found to update.'

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, AD_UNIT_ID, TEAM_ID)
