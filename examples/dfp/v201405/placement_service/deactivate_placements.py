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

"""This code example deactivates all active placements.

To determine which placements exist, run get_all_placements.py.
"""

__author__ = ('Nicholas Chen',
              'Joseph DiLallo')

# Import appropriate modules from the client library.
from googleads import dfp

PLACEMENT_ID = 'INSERT_PLACEMENT_ID_HERE'


def main(client, placement_id):
  # Initialize appropriate service.
  placement_service = client.GetService('PlacementService', version='v201405')

  # Create query.
  values = [{
      'key': 'placementId',
      'value': {
          'xsi_type': 'NumberValue',
          'value': placement_id
      }
  }]
  query = 'WHERE id = :placementId'
  statement = dfp.FilterStatement(query, values, 1)

  # Get placements by statement.
  placements = placement_service.getPlacementsByStatement(
      statement.ToStatement())

  for placement in placements:
    print ('Placement with id \'%s\', name \'%s\', and status \'%s\' will be '
           'deactivated.' % (placement['id'], placement['name'],
                             placement['status']))

  # Perform action.
  result = placement_service.performPlacementAction(
      {'xsi_type': 'DeactivatePlacements'}, statement.ToStatement())

  # Display results.
  if result and int(result['numChanges']) > 0:
    print 'Number of placements deactivated: %s' % result['numChanges']
  else:
    print 'No placements were deactivated.'

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, PLACEMENT_ID)
