#!/usr/bin/env python
#
# Copyright 2019 Google Inc. All Rights Reserved.
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
"""This example gets all targeting presets.
"""

# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  # Initialize appropriate service.
  targeting_preset_service = client.GetService(
      'TargetingPresetService', version='v202005')

  # Create a statement to select suggested ad units.
  statement = ad_manager.StatementBuilder(version='v202005')

  # Retrieve a small number of targeting presets at a time, paging
  # through until all targeting presets have been retrieved.
  while True:
    response = targeting_preset_service.getTargetingPresetsByStatement(
        statement.ToStatement())
    if 'results' in response and len(response['results']):
      for targeting_preset in response['results']:
        # Print out some information for each targeting preset.
        print(
            'Targeting preset with ID "%s" and name "%d" was found.\n'
            % (targeting_preset['id'], targeting_preset['name']))
      statement.offset += statement.limit
    else:
      break

  print('\nNumber of results found: %s' % response['totalResultSetSize'])


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
