#!/usr/bin/env python
#
# Copyright 2019 Google LLC
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

"""This example adds a historical adjustment of 110% for New Years Day traffic.
"""

from __future__ import print_function
import datetime

# Import appropriate modules from the client library.
from googleads import ad_manager

ADJUSTMENT_ID = 'INSERT_ADJUSTMENT_ID_HERE'


def main(client, adjustment_id):
  # Initialize the adjustment service.
  adjustment_service = client.GetService('AdjustmentService', version='v201902')

  # Create a statement to select a single traffic forecast adjustment by id.
  statement = (
      ad_manager.StatementBuilder(
          version='v201902').Where('id = :id').WithBindVariable(
              'id', adjustment_id))

  # Get the forecast traffic adjustment.
  response = adjustment_service.getTrafficAdjustmentsByStatement(
      statement.ToStatement())

  # Create a new historical adjustment segment for New Year's Day.
  this_new_years = datetime.date(datetime.date.today().year, 12, 31)
  next_new_years = datetime.date(datetime.date.today().year + 1, 12, 31)

  new_years_segment = {
      'basisType': 'HISTORICAL',
      'historicalAdjustment': {
          'targetDateRange': {
              'startDate': next_new_years,
              'endDate': next_new_years
          },
          'referenceDateRange': {
              'startDate': this_new_years,
              'endDate': this_new_years
          },
          'milliPercentMultiplier': 110000
      }
  }

  if 'results' in response and len(response['results']):
    # Update each local traffic adjustment.
    updated_adjustments = []
    for adjustment in response['results']:
      adjustment['forecastAdjustmentSegments'].append(new_years_segment)
      updated_adjustments.append(adjustment)

    # Update traffic adjustments remotely.
    adjustments = adjustment_service.updateTrafficAdjustments(
        updated_adjustments)

    # Display the results.
    if adjustments:
      for adjustment in adjustments:
        print('Traffic forecast adjustment with id %d and %d segments was '
              'created.' % (adjustment['id'],
                            len(adjustment['forecastAdjustmentSegments'])))
    else:
      print('No traffic adjustments were updated.')
  else:
    print('No traffic adjustments found to update.')


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, ADJUSTMENT_ID)
