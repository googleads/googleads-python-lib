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

"""This code example approves all eligible draft and pending orders.

To determine which orders exist, run get_all_orders.py.
"""


import datetime

# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  # Initialize appropriate service.
  order_service = client.GetService('OrderService', version='v202502')

  # Create a filter statement.
  today = datetime.date.today()
  statement = (ad_manager.StatementBuilder(version='v202502')
               .Where(('status in (\'DRAFT\', \'PENDING_APPROVAL\') '
                       'AND endDateTime >= :today AND isArchived = FALSE'))
               .WithBindVariable('today', today))
  orders_approved = 0

  # Get orders by statement.
  while True:
    response = order_service.getOrdersByStatement(statement.ToStatement())
    if 'results' in response and len(response['results']):
      # Display results.
      for order in response['results']:
        print('Order with id "%s", name "%s", and status "%s" will be '
              'approved.' % (order['id'], order['name'], order['status']))
      # Perform action.
      result = order_service.performOrderAction(
          {'xsi_type': 'ApproveOrders'}, statement.ToStatement())
      if result and int(result['numChanges']) > 0:
        orders_approved += int(result['numChanges'])
      statement.offset += statement.limit
    else:
      break

  # Display results.
  if orders_approved > 0:
    print('Number of orders approved: %s' % orders_approved)
  else:
    print('No orders were approved.')

if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
