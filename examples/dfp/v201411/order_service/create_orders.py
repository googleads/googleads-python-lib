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

"""This code example creates new orders.

To determine which orders exist, run get_all_orders.py."""


import uuid

# Import appropriate modules from the client library.
from googleads import dfp

COMPANY_ID = 'INSERT_ADVERTISER_COMPANY_ID_HERE'
SALESPERSON_ID = 'INSERT_SALESPERSON_ID_HERE'
TRAFFICKER_ID = 'INSERT_TRAFFICKER_ID_HERE'


def main(client, company_id, salesperson_id, trafficker_id):
  # Initialize appropriate service.
  order_service = client.GetService('OrderService', version='v201411')

  # Create order objects.
  orders = []
  for i in xrange(5):
    order = {
        'name': 'Order #%s' % uuid.uuid4(),
        'advertiserId': company_id,
        'salespersonId': salesperson_id,
        'traffickerId': trafficker_id
    }
    orders.append(order)

  # Add orders.
  orders = order_service.createOrders(orders)

  # Display results.
  for order in orders:
    print ('Order with id \'%s\' and name \'%s\' was created.'
           % (order['id'], order['name']))

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, COMPANY_ID, SALESPERSON_ID, TRAFFICKER_ID)
