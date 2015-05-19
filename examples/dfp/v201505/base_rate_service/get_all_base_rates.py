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

"""This example gets all base rates.

To create product base rates, run create_product_base_rates.py
To create product template base rates, run
create_product_template_base_rates.py.

Tags: BaseRateService.getBaseRatesByStatement
"""

__author__ = 'Nicholas Chen'

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  base_rate_service = client.GetService('BaseRateService', version='v201505')

  # Create a filter statement.
  statement = dfp.FilterStatement('ORDER BY id ASC')

  # Get base rates by statement.
  while True:
    response = base_rate_service.getBaseRatesByStatement(
        statement.ToStatement())
    if 'results' in response:
      # Display results.
      for base_rate in response['results']:
        print ('Base rate with ID \'%s\' and type \'%s\' belonging to '
               'rate card ID \'%s\' was found.' % (
                   base_rate['id'],
                   dfp.DfpClassType(base_rate),
                   base_rate['rateCardId']))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
