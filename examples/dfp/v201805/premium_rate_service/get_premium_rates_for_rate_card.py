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
"""This example gets all premium rates on a specific rate card.
"""

# Import appropriate modules from the client library.
from googleads import dfp

RATE_CARD_ID = 'INSERT_RATE_CARD_ID_HERE'


def main(client, rate_card_id):
  # Initialize appropriate service.
  premium_rate_service = client.GetService(
      'PremiumRateService', version='v201805')
  # Create a statement to select premium rates.
  statement = (dfp.StatementBuilder()
               .Where('rateCardId = :rateCardId')
               .WithBindVariable('rateCardId', rate_card_id))

  # Retrieve a small amount of premium rates at a time, paging
  # through until all premium rates have been retrieved.
  while True:
    response = premium_rate_service.getPremiumRatesByStatement(
        statement.ToStatement())
    if 'results' in response and len(response['results']):
      for premium_rate in response['results']:
        # Print out some information for each premium rate.
        print('Premium rate with ID "%d", premium feature "%s", and rate card '
              'ID "%d" was found.\n' % (premium_rate['id'],
                                        premium_rate['premium feature'],
                                        premium_rate['rateCardId']))
      statement.offset += statement.limit
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, RATE_CARD_ID)
