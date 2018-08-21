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

"""This code example updates a single placement to allow for AdSense targeting.

To determine which placements exist, run get_all_placements.py.
"""


# Import appropriate modules from the client library.
from googleads import ad_manager

PLACEMENT_ID = 'INSERT_PLACEMENT_ID_HERE'


def main(client, placement_id):
  # Initialize appropriate service.
  placement_service = client.GetService('PlacementService', version='v201802')

  # Create query.
  statement = (ad_manager.StatementBuilder()
               .Where('id = :id')
               .OrderBy('id', ascending=True)
               .Limit(1)
               .WithBindVariable('id', placement_id))

  # Get placements by statement.
  page = placement_service.getPlacementsByStatement(
      statement.ToStatement())

  placement = page['results'][0]

  placement['description'] = 'This placement contains all leaderboards.'

  # Update placements remotely.
  updated_placements = placement_service.updatePlacements([placement])

  for placement in updated_placements:
    print ('Placement with id "%s" and name "%s" was updated.'
           % (placement['id'], placement['name']))

if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, PLACEMENT_ID)
