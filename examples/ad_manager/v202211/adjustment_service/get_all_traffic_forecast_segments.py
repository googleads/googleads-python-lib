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

"""This example gets all traffic forecast segments."""

# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  # Initialize the adjustment service.
  adjustment_service = client.GetService('AdjustmentService', version='v202211')

  # Create a statement to get all traffic forecast segments.
  statement = ad_manager.StatementBuilder(version='v202211')

  # Retrieve a small number of segments at a time, paging through until all
  # segments have been retrieved.
  while True:
    response = adjustment_service.getTrafficForecastSegmentsByStatement(
        statement.ToStatement())
    if 'results' in response and len(response['results']):
      for segment in response['results']:
        # Print out some information for each traffic forecast segment.
        print('Traffic forecast segment with id %d and name "%s" was found ' % (
            segment['id'], segment['name'],
        ))
      statement.offset += statement.limit
    else:
      break

  print('\nNumber of results found: %s' % response['totalResultSetSize'])


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
