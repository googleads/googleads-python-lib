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

"""This example populates a specific first party audience segment.

To determine which first party audience segments exist, run
get_first_party_audience_segments.py.
"""


# Import appropriate modules from the client library.
from googleads import dfp

AUDIENCE_SEGMENT_ID = 'INSERT_AUDIENCE_SEGMENT_ID_HERE'


def main(client, audience_segment_id):
  # Initialize appropriate service.
  audience_segment_service = client.GetService(
      'AudienceSegmentService', version='v201711')

  # Create statement object to get the specified first party audience segment.
  statement = (dfp.StatementBuilder()
               .Where('Type = :type AND Id = :audience_segment_id')
               .WithBindVariable('audience_segment_id',
                                 long(audience_segment_id))
               .WithBindVariable('type', 'FIRST_PARTY')
               .Limit(1))

  response = audience_segment_service.getAudienceSegmentsByStatement(
      statement.ToStatement())

  if 'results' in response and len(response['results']):
    segments = response['results']

    for segment in segments:
      print (
          'Audience segment with id "%s" and name "%s" will be populated.'
          % (segment['id'], segment['name']))

    action = {
        'xsi_type': 'PopulateAudienceSegments'
    }

    populated_audience_segments = (
        audience_segment_service.performAudienceSegmentAction(
            action, statement.ToStatement()))

    print ('%s audience segment populated' %
           populated_audience_segments['numChanges'])
  else:
    print 'No Results Found'


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, AUDIENCE_SEGMENT_ID)
