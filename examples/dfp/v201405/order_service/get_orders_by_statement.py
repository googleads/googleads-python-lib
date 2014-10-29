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

"""This code example gets an order by an ID.

To create orders, run create_orders.py."""

__author__ = ('Nicholas Chen',
              'Joseph DiLallo')

# Import appropriate modules from the client library.
from googleads import dfp

# Set id of the order to get.
ORDER_ID = 'INSERT_ORDER_ID_HERE'


def main(client, order_id):
  # Initialize appropriate service.
  order_service = client.GetService('OrderService', version='v201405')

  # Create statement object to select a single order by an ID.
  values = [{
      'key': 'orderId',
      'value': {
          'xsi_type': 'NumberValue',
          'value': order_id
      }
  }]
  query = 'WHERE id = :orderId'

  statement = dfp.FilterStatement(query, values)

  # Get orders by statement.
  response = order_service.getOrdersByStatement(statement.ToStatement())
  orders = []
  if 'results' in response:
    orders = response['results']

  # Display results.
  for order in orders:
    print ('Order with id \'%s\' name \'%s\' was found.'
           % (order['id'], order['name']))

  print '\nNumber of results found: %s' % len(orders)

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, ORDER_ID)
