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

"""This example updates the value of an exchange rate.

To create exchange rates, run create_exchange_rates.py.

"""


# Import appropriate modules from the client library.
from googleads import ad_manager

EXCHANGE_RATE_ID = 'INSERT_EXCHANGE_RATE_ID_HERE'


def main(client, exchange_rate_id):
  # Initialize appropriate service.
  exchange_rate_service = client.GetService('ExchangeRateService',
                                            version='v201905')

  # Create a statement to get an exchange rate by its ID.
  statement = (ad_manager.StatementBuilder(version='v201905')
               .Where('id = :id')
               .WithBindVariable('id', long(exchange_rate_id))
               .Limit(1))

  # Get rate cards by statement.
  response = exchange_rate_service.getExchangeRatesByStatement(
      statement.ToStatement())

  if 'results' in response and len(response['results']):
    exchange_rate = response['results'][0]

    # Update the exchange rate value to 1.5.
    exchange_rate['exchangeRate'] = long(15000000000)

    exchange_rates = exchange_rate_service.updateExchangeRates([exchange_rate])

    if exchange_rates:
      for exchange_rate in exchange_rates:
        print ('Exchange rate with id \'%s,\' currency code \'%s,\' '
               'direction \'%s,\' and exchange rate \'%.2f\' '
               'was updated.' % (exchange_rate['id'],
                                 exchange_rate['currencyCode'],
                                 exchange_rate['direction'],
                                 (float(exchange_rate['exchangeRate']) /
                                  10000000000)))
    else:
      print 'No exchange rates were updated.'
  else:
    print 'No exchange rates found to update.'


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, EXCHANGE_RATE_ID)
