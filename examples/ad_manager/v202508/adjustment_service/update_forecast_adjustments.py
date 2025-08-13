#!/usr/bin/env python
#
# Copyright 2020 Google LLC
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

"""This example updates a forecast adjustment's name."""

# Import appropriate modules from the client library.
from googleads import ad_manager

ADJUSTMENT_ID = 'INSERT_ADJUSTMENT_ID_HERE'


def main(client, adjustment_id):
  # Initialize the adjustment service.
  adjustment_service = client.GetService('AdjustmentService', version='v202508')

  # Create a statement to select a single forecast adjustment by id.
  statement = (
      ad_manager.StatementBuilder(
          version='v202508').Where('id = :id').WithBindVariable(
              'id', adjustment_id))

  # Get the forecast adjustment.
  response = adjustment_service.getForecastAdjustmentsByStatement(
      statement.ToStatement())

  if 'results' in response and len(response['results']):
    # Update each local forecast adjustment's name.
    updated_adjustments = []
    for adjustment in response['results']:
      adjustment['name'] += ' (updated)'
      updated_adjustments.append(adjustment)

    # Update the forecast adjustment on the server.
    adjustments = adjustment_service.updateForecastAdjustments(
        updated_adjustments)

    # Display the results.
    if adjustments:
      for adjustment in adjustments:
        print('Forecast adjustment with id %d and name "%s" was updated' % (
            adjustment['id'], adjustment['name']))
    else:
      print('No forecast adjustments were updated.')
  else:
    print('No forecast adjustments found to update.')


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, ADJUSTMENT_ID)
