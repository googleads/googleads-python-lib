#!/usr/bin/env python
#
# Copyright 2017 Google Inc. All Rights Reserved.
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

"""This example pauses a line item.

Line items must be paused before they can be updated. To determine which line
items exist, run get_all_line_items.py
"""

# Import appropriate modules from the client library.
from googleads import ad_manager

# Set the ID of the line item to pause.
LINE_ITEM_ID = 'INSERT_LINE_ITEM_ID_HERE'


def main(client):
  # Initialize appropriate service.
  line_item_service = client.GetService('LineItemService', version='v202505')

  # Create a statement to select the line item.
  # Change this to operate on more than one Line Item.
  statement = (ad_manager.StatementBuilder(version='v202505')
               .Where('id = :id')
               .OrderBy('id', ascending=True)
               .WithBindVariable('id', LINE_ITEM_ID))

  result_set_size = 0
  should_continue = True

  # Iterate over paged results from the statement.
  while should_continue:
    page = line_item_service.getLineItemsByStatement(statement.ToStatement())
    if 'results' in page and len(page['results']):
      result_set_size = page['totalResultSetSize']
      # Iterate over individual results in the page.
      for line_item in page['results']:
        print('Pausing line item with ID %d' % line_item['id'])
    # Update statement for next page.
    statement.offset += statement.limit
    should_continue = statement.offset < result_set_size

  print('Pausing %d line item(s)' % result_set_size)

  if result_set_size > 0:
    statement.offset = None
    statement.limit = None

    # Perform Pause action on all Line Items that match the statement.
    update_result = line_item_service.performLineItemAction(
        {'xsi_type': 'PauseLineItems'}, statement.ToStatement())

    if update_result and update_result['numChanges'] > 0:
      print('Updated %d line item(s)' % update_result['numChanges'])
    else:
      print('No line items were paused')

if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
