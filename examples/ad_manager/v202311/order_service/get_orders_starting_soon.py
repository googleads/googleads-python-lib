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
"""This example gets all orders that are starting soon.
"""

# Import appropriate modules from the client library.
from datetime import datetime
from datetime import timedelta

from googleads import ad_manager
import pytz


def main(client):
  # Initialize appropriate service.
  order_service = client.GetService('OrderService', version='v202311')
  now = datetime.now(tz=pytz.timezone('America/New_York'))
  soon = now + timedelta(days=5)

  # Create a statement to select orders.
  statement = (ad_manager.StatementBuilder(version='v202311')
               .Where(('status = :status AND startDateTime >= :now '
                       'AND startDateTime <= :soon'))
               .WithBindVariable('status', 'APPROVED')
               .WithBindVariable('now', now)
               .WithBindVariable('soon', soon))

  # Retrieve a small amount of orders at a time, paging
  # through until all orders have been retrieved.
  while True:
    response = order_service.getOrdersByStatement(statement.ToStatement())
    if 'results' in response and len(response['results']):
      for order in response['results']:
        # Print out some information for each order.
        print('Order with ID "%d" and name "%s" was found.\n' % (order['id'],
                                                                 order['name']))
      statement.offset += statement.limit
    else:
      break

  print('\nNumber of results found: %s' % response['totalResultSetSize'])


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
