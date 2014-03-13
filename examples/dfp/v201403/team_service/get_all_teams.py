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

"""This example gets all teams.

To create teams, run create_teams.py.

Tags: TeamService.getTeamsByStatement
"""

__author__ = ('Nicholas Chen',
              'Joseph DiLallo')

# Import appropriate classes from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  team_service = client.GetService('TeamService', version='v201403')

  # Create a filter statement.
  statement = dfp.FilterStatement()

  # Get users by statement.
  while True:
    response = team_service.getTeamsByStatement(statement.ToStatement())
    if 'results' in response:
      # Display results.
      for team in response['results']:
        print ('Team with ID \'%s\' and name \'%s\' was found.'
               % (team['id'], team['name']))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
