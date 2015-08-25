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

"""This code example gets all exchange rates.

To create exchange rates, run create_exchange_rates.py.

"""


# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  exchange_rate_service = client.GetService('ExchangeRateService',
                                            version='v201411')

  # Create a filter statement.
  statement = dfp.FilterStatement('ORDER BY id ASC')

  # Get all exchange rates by statement.
  while True:
    response = exchange_rate_service.getExchangeRatesByStatement(
        statement.ToStatement())
    if 'results' in response:
      # Display results.
      for exchange_rate in response['results']:
        print ('Exchange rate with id \'%s,\' currency code \'%s,\' '
               'direction \'%s,\' and exchange rate \'%.2f\' '
               'was found.' % (exchange_rate['id'],
                               exchange_rate['currencyCode'],
                               exchange_rate['direction'],
                               (float(exchange_rate['exchangeRate']) /
                                10000000000)))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
