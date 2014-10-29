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

"""This example creates new teams.

To determine which teams exist, run get_all_teams.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: TeamService.createTeams
"""

__author__ = ('Nicholas Chen',
              'Joseph DiLallo')

import uuid

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  team_service = client.GetService('TeamService', version='v201405')

  # Create team objects.
  teams = []
  for i in xrange(5):
    team = {
        'name': 'Team %s' % uuid.uuid4(),
        'hasAllCompanies': 'false',
        'hasAllInventory': 'false',
        'teamAccessType': 'READ_WRITE'
    }
    teams.append(team)

  # Add Teams.
  teams = team_service.createTeams(teams)

  # Display results.
  for team in teams:
    print ('Team with ID \'%s\' and name \'%s\' was created.'
           % (team['id'], team['name']))

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
