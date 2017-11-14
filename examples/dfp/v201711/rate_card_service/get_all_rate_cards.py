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
"""This example gets all rate cards.
"""

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  rate_card_service = client.GetService('RateCardService', version='v201711')

  # Create a statement to select rate cards.
  statement = dfp.StatementBuilder()

  # Retrieve a small amount of rate cards at a time, paging
  # through until all rate cards have been retrieved.
  while True:
    response = rate_card_service.getRateCardsByStatement(statement.ToStatement(
    ))
    if 'results' in response:
      for rate_card in response['results']:
        # Print out some information for each rate card.
        print('Rate card with ID "%d", name "%s", and currency code "%s" was '
              'found.\n' %
              (rate_card['id'], rate_card['name'], rate_card['currencyCode']))
      statement.offset += statement.limit
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
