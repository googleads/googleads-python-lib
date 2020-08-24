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

"""This code example updates the notes of a single order specified by ID.

To determine which orders exist, run get_all_orders.py.
"""


# Import appropriate modules from the client library.
from googleads import ad_manager

ORDER_ID = 'INSERT_ORDER_ID_HERE'


def main(client, order_id):
  # Initialize appropriate service.
  order_service = client.GetService('OrderService', version='v202008')

  # Create statement object to select a single order by an ID.

  statement = (ad_manager.StatementBuilder(version='v202008')
               .Where('id = :orderId')
               .WithBindVariable('orderId', int(order_id)))

  # Get orders by statement.
  response = order_service.getOrdersByStatement(statement.ToStatement())

  if 'results' in response and len(response['results']):
    # Update each local order object by changing its notes.
    updated_orders = []
    for order in response['results']:
      # Archived orders cannot be updated.
      if not order['isArchived']:
        order['notes'] = 'Spoke to advertiser. All is well.'
        updated_orders.append(order)

    # Update orders remotely.
    orders = order_service.updateOrders(updated_orders)

    # Display results.
    if orders:
      for order in orders:
        print('Order with id "%s", name "%s", advertiser id "%s", and '
              'notes "%s" was updated.'
              % (order['id'], order['name'], order['advertiserId'],
                  order['notes']))
    else:
      print('No orders were updated.')
  else:
    print('No orders found to update.')


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, ORDER_ID)

