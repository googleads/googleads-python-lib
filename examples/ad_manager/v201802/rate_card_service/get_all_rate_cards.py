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
from googleads import ad_manager


def main(client):
  # Initialize appropriate service.
  rate_card_service = client.GetService('RateCardService', version='v201802')

  # Create a statement to select rate cards.
  statement = ad_manager.StatementBuilder()

  # Retrieve a small amount of rate cards at a time, paging
  # through until all rate cards have been retrieved.
  while True:
    response = rate_card_service.getRateCardsByStatement(statement.ToStatement(
    ))
    if 'results' in response and len(response['results']):
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
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
