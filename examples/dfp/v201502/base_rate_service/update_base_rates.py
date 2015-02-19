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

"""This example updates a base rate's value.

To determine which base rates exist, run get_all_base_rates.py.

Tags: BaseRateService.getBaseRatesByStatement
Tags: BaseRateService.updateBaseRates
"""

__author__ = 'Nicholas Chen'

# Import appropriate modules from the client library.
from googleads import dfp

BASE_RATE_ID = 'INSERT_BASE_RATE_ID_HERE'


def main(client, base_rate_id):
  # Initialize appropriate service.
  base_rate_service = client.GetService('BaseRateService', version='v201502')

  # Create a filter statement for base rates for a single rate card.
  values = [{
      'key': 'id',
      'value': {
          'xsi_type': 'NumberValue',
          'value': base_rate_id
      }
  }]
  query = 'where id = :id ORDER BY id ASC'
  statement = dfp.FilterStatement(query, values, 1)

  # Get single base rate by statement.
  response = base_rate_service.getBaseRatesByStatement(
      statement.ToStatement())

  if 'results' in response:
    # Update each local base rate object by changing its value to $3 USD.
    new_rate = {
        'currencyCode': 'USD',
        'microAmount': 3000000
    }

    updated_base_rates = []
    for base_rate in response['results']:
      base_rate['rate'] = new_rate
      updated_base_rates.append(base_rate)

    # Update base rates remotely.
    base_rates = base_rate_service.updateBaseRates(updated_base_rates)

    # Display results.
    if base_rates:
      for base_rate in base_rates:
        print ('Base rate with ID \'%s\' and type \'%s\' belonging to '
               'rate card ID \'%s\' was updated.' % (
                   base_rate['id'],
                   dfp.DfpClassType(base_rate),
                   base_rate['rateCardId']))
    else:
      print 'No base rates were updated.'
  else:
    print 'No base rates found to update.'


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, BASE_RATE_ID)
