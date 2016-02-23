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

"""This code example shows how to get recently updated line items.

To create line items, run create_line_items.py."""


import datetime

# Import appropriate modules from the client library.
from googleads import dfp

ORDER_ID = 'INSERT_ORDER_ID_HERE'


def main(client, order_id):
  # Initialize appropriate service.
  line_item_service = client.GetService('LineItemService', version='v201602')

  # Create statement object to only select line items belonging to the order and
  # have been modified in the last 3 days.
  three_days_ago = datetime.date.today() - datetime.timedelta(days=3)
  values = [{
      'key': 'dateTimeString',
      'value': {
          'xsi_type': 'TextValue',
          'value': three_days_ago.strftime('%Y-%m-%dT%H:%M:%S')
      }
  }, {
      'key': 'orderId',
      'value': {
          'xsi_type': 'NumberValue',
          'value': order_id
      }
  }]
  query = 'WHERE lastModifiedDateTime >= :dateTimeString AND orderId = :orderId'
  statement = dfp.FilterStatement(query, values)

  while True:
    # Get line items by statement.
    response = line_item_service.getLineItemsByStatement(
        statement.ToStatement())

    if 'results' in response:
      # Display results.
      for line_item in response['results']:
        print ('Line item with id \'%s\', belonging to order id \'%s\', and '
               'named \'%s\' was found.' % (line_item['id'],
                                            line_item['orderId'],
                                            line_item['name']))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, ORDER_ID)
