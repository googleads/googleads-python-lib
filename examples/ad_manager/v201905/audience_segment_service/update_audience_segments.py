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

"""This example updates rule based first party audience segments.

To determine which audience segments exist, run get_all_audience_segments.py.
"""


# Import appropriate modules from the client library.
from googleads import ad_manager

AUDIENCE_SEGMENT_ID = 'INSERT_AUDIENCE_SEGMENT_ID_HERE'


def main(client, audience_segment_id):
  # Initialize appropriate service.
  audience_segment_service = client.GetService(
      'AudienceSegmentService', version='v201905')

  # Create statement object to get the specified first party audience segment.
  statement = (ad_manager.StatementBuilder(version='v201905')
               .Where('Type = :type AND Id = :audience_segment_id')
               .WithBindVariable('audience_segment_id',
                                 int(audience_segment_id))
               .WithBindVariable('type', 'FIRST_PARTY')
               .Limit(1))

  # Get audience segments by statement.
  response = audience_segment_service.getAudienceSegmentsByStatement(
      statement.ToStatement())

  if 'results' in response and len(response['results']):
    updated_audience_segments = []
    for audience_segment in response['results']:
      print('Audience segment with id "%s" and name "%s" will be updated.'
            % (audience_segment['id'], audience_segment['name']))

      audience_segment['membershipExpirationDays'] = '180'
      updated_audience_segments.append(audience_segment)

    audience_segments = audience_segment_service.updateAudienceSegments(
        updated_audience_segments)

    for audience_segment in audience_segments:
      print('Audience segment with id "%s" and name "%s" was updated' %
            (audience_segment['id'], audience_segment['name']))
  else:
    print('No audience segment found to update.')


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, AUDIENCE_SEGMENT_ID)
