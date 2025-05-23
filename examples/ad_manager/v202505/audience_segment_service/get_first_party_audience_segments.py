#!/usr/bin/env python
#
# Copyright 2016 Google Inc. All Rights Reserved.
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
"""This example gets all first party audience segments.
"""

# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  # Initialize appropriate service.
  audience_segment_service = client.GetService(
      'AudienceSegmentService', version='v202505')
  # Create a statement to select audience segments.
  statement = (ad_manager.StatementBuilder(version='v202505')
               .Where('type = :type')
               .WithBindVariable('type', 'FIRST_PARTY'))

  # Retrieve a small amount of audience segments at a time, paging
  # through until all audience segments have been retrieved.
  while True:
    response = audience_segment_service.getAudienceSegmentsByStatement(
        statement.ToStatement())
    if 'results' in response and len(response['results']):
      for audience_segment in response['results']:
        # Print out some information for each audience segment.
        print('Audience segment with ID "%d", name "%s", and size "%d" was '
              'found.\n' % (audience_segment['id'], audience_segment['name'],
                            audience_segment['size']))
      statement.offset += statement.limit
    else:
      break

  print('\nNumber of results found: %s' % response['totalResultSetSize'])


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
