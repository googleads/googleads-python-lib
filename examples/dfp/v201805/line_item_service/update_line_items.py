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

"""This code example updates the delivery rate of all line items in an order.

To determine which line items exist, run get_all_line_items.py.
"""


# Import appropriate modules from the client library.
from googleads import dfp

# Set id of the order to get line items from.
ORDER_ID = 'INSERT_ORDER_ID_HERE'


def main(client, order_id):
  # Initialize appropriate service.
  line_item_service = client.GetService('LineItemService', version='v201805')

  # Create statement object to only select line items with even delivery rates.

  statement = (dfp.StatementBuilder()
               .Where(('deliveryRateType = :deliveryRateType AND '
                       'orderId = :orderId'))
               .WithBindVariable('orderId', long(order_id))
               .WithBindVariable('deliveryRateType', 'EVENLY')
               .Limit(500))

  # Get line items by statement.
  response = line_item_service.getLineItemsByStatement(
      statement.ToStatement())

  if 'results' in response:
    # Update each local line item by changing its delivery rate type.
    updated_line_items = []
    for line_item in response['results']:
      if not line_item['isArchived']:
        line_item['deliveryRateType'] = 'AS_FAST_AS_POSSIBLE'
        updated_line_items.append(line_item)

    # Update line items remotely.
    line_items = line_item_service.updateLineItems(updated_line_items)

    # Display results.
    if line_items:
      for line_item in line_items:
        print ('Line item with id "%s", belonging to order id "%s", named '
               '"%s", and delivery rate "%s" was updated.'
               % (line_item['id'], line_item['orderId'], line_item['name'],
                  line_item['deliveryRateType']))
    else:
      print 'No line items were updated.'
  else:
    print 'No line items found to update.'


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, ORDER_ID)
