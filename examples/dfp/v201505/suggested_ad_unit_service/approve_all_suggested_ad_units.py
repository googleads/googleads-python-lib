#!/usr/bin/python
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

"""This code example approves all suggested ad units with 50 or more requests.

This feature is only available to DFP premium solution networks.
"""


# Import appropriate modules from the client library.
from googleads import dfp

THRESHOLD_NUMBER_OF_REQUESTS = '50'


def main(client):
    # Initialize appropriate service.
  suggested_ad_unit_service = client.GetService(
      'SuggestedAdUnitService', version='v201505')

  values = [{
      'key': 'numRequests',
      'value': {
          'xsi_type': 'NumberValue',
          'value': THRESHOLD_NUMBER_OF_REQUESTS
      }
  }]

  query = 'WHERE numRequests > :numRequests'

  # Create a filter statement.
  statement = dfp.FilterStatement(query, values)
  num_approved_suggested_ad_units = 0

  # Get suggested ad units by statement.
  while True:
    response = suggested_ad_unit_service.getSuggestedAdUnitsByStatement(
        statement.ToStatement())
    if 'results' in response:
      # Print suggested ad units that will be approved.
      for suggested_ad_unit in response['results']:
        print ('Suggested ad unit with id \'%s\', and number of requests \'%s\''
               ' will be approved.' % (suggested_ad_unit['id'],
                                       suggested_ad_unit['numRequests']))

      # Approve suggested ad units.
      result = suggested_ad_unit_service.performSuggestedAdUnitAction(
          {'xsi_type': 'ApproveSuggestedAdUnit'},
          statement.ToStatement())
      if result and int(result['numChanges']) > 0:
        num_approved_suggested_ad_units += int(result['numChanges'])
    else:
      break

  if num_approved_suggested_ad_units > 0:
    print ('Number of suggested ad units approved: %s' %
           num_approved_suggested_ad_units)
  else:
    print 'No suggested ad units were approved.'

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)

