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

"""This example creates an exchange rate.

To determine which exchange rates exist, run get_all_exchange_rates.py.


"""


# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  exchange_rate_service = client.GetService('ExchangeRateService',
                                            version='v201602')

  # Create a new fixed exchange rate with currency code 'AUD', with direction
  # FROM_NETWORK with a value of 1.5.
  exchange_rate = {
      'currencyCode': 'AUD',
      'direction': 'FROM_NETWORK',
      'exchangeRate': long(15000000000),
      'refreshRate': 'FIXED'
  }

  created_exchange_rate = exchange_rate_service.createExchangeRates(
      [exchange_rate])[0]

  print ('Exchange rate with id \'%s,\' currency code \'%s,\' '
         'direction \'%s,\' and exchange rate \'%.2f\' '
         'was created.' % (created_exchange_rate['id'],
                           created_exchange_rate['currencyCode'],
                           created_exchange_rate['direction'],
                           (float(created_exchange_rate['exchangeRate']) /
                            10000000000)))


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
