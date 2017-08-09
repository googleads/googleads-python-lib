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
"""This example gets all exchange rates.
"""

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  exchange_rate_service = client.GetService(
      'ExchangeRateService', version='v201705')

  # Create a statement to select exchange rates.
  statement = dfp.StatementBuilder()

  # Retrieve a small amount of exchange rates at a time, paging
  # through until all exchange rates have been retrieved.
  while True:
    response = exchange_rate_service.getExchangeRatesByStatement(
        statement.ToStatement())
    if 'results' in response:
      for exchange_rate in response['results']:
        # Print out some information for each exchange rate.
        print(
            'Exchange rate with ID "%d", currency code "%s", direction "%s",  '
            'and exchange rate "%d" was found.\n' %
            (exchange_rate['id'], exchange_rate['currencyCode'],
             exchange_rate['direction'], exchange_rate['exchangeRate']))
      statement.offset += statement.limit
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
