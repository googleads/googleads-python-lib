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

from googleads import dfp


def main(client):
  # Initialize appropriate service.
  order_service = client.GetService('OrderService', version='v201611')
  query = ('WHERE status = :status and startDateTime >= :now and startDateTime '
           '<= :soon')
  values = [
      {'key': 'status',
       'value': {
           'xsi_type': 'TextValue',
           'value': 'APPROVED'
       }},
      {'key': 'now',
       'value': {
           'xsi_type': 'TextValue',
           'value': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
       }},
      {'key': 'soon',
       'value': {
           'xsi_type': 'TextValue',
           'value': (datetime.now() + timedelta(days=5))
                    .strftime('%Y-%m-%dT%H:%M:%S')
       }},
  ]
  # Create a statement to select orders.
  statement = dfp.FilterStatement(query, values)

  # Retrieve a small amount of orders at a time, paging
  # through until all orders have been retrieved.
  while True:
    response = order_service.getOrdersByStatement(statement.ToStatement())
    if 'results' in response:
      for order in response['results']:
        # Print out some information for each order.
        print('Order with ID "%d" and name "%s" was found.\n' % (order['id'],
                                                                 order['name']))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
