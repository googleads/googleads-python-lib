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

"""This example gets all traffic adjustments."""

from __future__ import print_function

# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  # Initialize the adjustment service.
  adjustment_service = client.GetService('AdjustmentService', version='v201911')

  # Create a statement to get all forecast traffic adjustments.
  statement = ad_manager.StatementBuilder(version='v201911')

  # Retrieve a small number of traffic adjustments at a time, paging
  # through until all traffic adjustments have been retrieved.
  while True:
    response = adjustment_service.getTrafficAdjustmentsByStatement(
        statement.ToStatement())
    if 'results' in response and len(response['results']):
      for adjustment in response['results']:
        # Print out some information for each traffic adjustment.
        print('Traffic forecast adjustment with id %d and %d segments was '
              'found.' % (adjustment['id'],
                          len(adjustment['forecastAdjustmentSegments'])))
      statement.offset += statement.limit
    else:
      break

  print('\nNumber of results found: %s' % response['totalResultSetSize'])


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
