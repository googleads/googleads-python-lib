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

"""This code example gets all premium rates belonging to a specific rate card.

To create premium rates, run create_premium_rates.py.

"""


# Import appropriate modules from the client library.
from googleads import dfp

RATE_CARD_ID = 'INSERT_RATE_CARD_ID_HERE'


def main(client, rate_card_id):
  # Initialize appropriate service.
  premium_rate_service = client.GetService('PremiumRateService',
                                           version='v201605')

  # Create statement object to select a single proposal by an ID.
  values = [{
      'key': 'rateCardId',
      'value': {
          'xsi_type': 'NumberValue',
          'value': rate_card_id
      }
  }]
  query = 'WHERE rateCardId = :rateCardId ORDER BY id ASC'
  statement = dfp.FilterStatement(query, values)

  # Get premium rates by statement.
  while True:
    response = premium_rate_service.getPremiumRatesByStatement(
        statement.ToStatement())
    if 'results' in response:
      # Display results.
      for premium_rate in response['results']:
        print ('Premium rate with ID \'%s\' of type \'%s\' assigned to '
               ' rate card with ID \'%s\' was found.\n' % (
                   premium_rate['id'],
                   dfp.DfpClassType(premium_rate['premiumFeature']),
                   premium_rate['rateCardId']))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, RATE_CARD_ID)
