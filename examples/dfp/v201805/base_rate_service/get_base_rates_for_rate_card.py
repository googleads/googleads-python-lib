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
"""This example gets all base rates belonging to a rate card.
"""

# Import appropriate modules from the client library.
from googleads import dfp

RATE_CARD_ID = 'INSERT_RATE_CARD_ID_HERE'


def main(client, rate_card_id):
  # Initialize appropriate service.
  base_rate_service = client.GetService('BaseRateService', version='v201805')
  # Create a statement to select base rates.
  statement = (dfp.StatementBuilder()
               .Where('rateCardId = :rateCardId')
               .WithBindVariable('rateCardId', rate_card_id))

  # Retrieve a small amount of base rates at a time, paging
  # through until all base rates have been retrieved.
  while True:
    response = base_rate_service.getBaseRatesByStatement(statement.ToStatement(
    ))
    if 'results' in response and len(response['results']):
      for base_rate in response['results']:
        # Print out some information for each base rate.
        print('Base rate with ID "%d", type "%s", and rate card ID "%d" was '
              'found.\n' %
              (base_rate['id'], dfp.DfpClassType(base_rate),
               base_rate['rateCardId']))
      statement.offset += statement.limit
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, RATE_CARD_ID)
