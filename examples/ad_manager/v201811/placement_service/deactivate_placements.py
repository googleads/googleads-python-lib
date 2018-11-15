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

"""This code example deactivates all active placements.

To determine which placements exist, run get_all_placements.py.
"""


# Import appropriate modules from the client library.
from googleads import ad_manager

PLACEMENT_ID = 'INSERT_PLACEMENT_ID_HERE'


def main(client, placement_id):
  # Initialize appropriate service.
  placement_service = client.GetService('PlacementService', version='v201811')

  # Create query.
  statement = (ad_manager.StatementBuilder(version='v201811')
               .Where('id = :placementId')
               .WithBindVariable('placementId', long(placement_id))
               .Limit(1))

  # Get placements by statement.
  placements = placement_service.getPlacementsByStatement(
      statement.ToStatement())

  for placement in placements:
    print ('Placement with id "%s", name "%s", and status "%s" will be '
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
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, PLACEMENT_ID)
