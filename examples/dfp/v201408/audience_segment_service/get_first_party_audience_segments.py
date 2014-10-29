#!/usr/bin/python
#
# Copyright 2014 Google Inc. All Rights Reserved.
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

"""This code example gets all first party audience segments.

To create first party audience segments, run create_audience_segments.py.
"""

__author__ = ('Nicholas Chen',
              'Joseph DiLallo')

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize client object.
  client = dfp.DfpClient.LoadFromStorage()

  # Initialize appropriate service.
  audience_segment_service = client.GetService(
      'AudienceSegmentService', version='v201408')

  # Create statement object to only select first party audience segments.
  values = [{
      'key': 'type',
      'value': {
          'xsi_type': 'TextValue',
          'value': 'FIRST_PARTY'
      }
  }]
  query = 'WHERE Type = :type'
  statement = dfp.FilterStatement(query, values)

  # Get audience segments by statement.
  while True:
    response = audience_segment_service.getAudienceSegmentsByStatement(
        statement.ToStatement())

    if 'results' in response:
      segments = response['results']
      for segment in segments:
        print ('Audience segment with id \'%s\' and name \'%s\' of size '
               '%s was found. ' %
               (segment['id'], segment['name'], segment['size']))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
