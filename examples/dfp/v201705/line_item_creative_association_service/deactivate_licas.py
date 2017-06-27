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

"""This code example deactivates all LICAs for the line item.

To determine which LICAs exist, run get_all_licas.py.
"""


# Import appropriate modules from the client library.
from googleads import dfp

# Set the id of the line item in which to deactivate LICAs.
LINE_ITEM_ID = 'INSERT_LINE_ITEM_ID_HERE'


def main(client, line_item_id):
  # Initialize appropriate service.
  lica_service = client.GetService(
      'LineItemCreativeAssociationService', version='v201705')

  # Create query.
  values = [{
      'key': 'lineItemId',
      'value': {
          'xsi_type': 'NumberValue',
          'value': line_item_id
      }
  }, {
      'key': 'status',
      'value': {
          'xsi_type': 'TextValue',
          'value': 'ACTIVE'
      }
  }]
  query = 'WHERE lineItemId = :lineItemId AND status = :status'
  statement = dfp.FilterStatement(query, values)

  num_deactivated_licas = 0

  # Get LICAs by statement.
  while True:
    response = lica_service.getLineItemCreativeAssociationsByStatement(
        statement.ToStatement())
    if 'results' in response:
      for lica in response['results']:
        print ('LICA with line item id "%s", creative id "%s", and status'
               ' "%s" will be deactivated.' %
               (lica['lineItemId'], lica['creativeId'], lica['status']))

      # Perform action.
      result = lica_service.performLineItemCreativeAssociationAction(
          {'xsi_type': 'DeactivateLineItemCreativeAssociations'},
          statement.ToStatement())
      if result and int(result['numChanges']) > 0:
        num_deactivated_licas += int(result['numChanges'])
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  # Display results.
  if num_deactivated_licas > 0:
    print 'Number of LICAs deactivated: %s' % num_deactivated_licas
  else:
    print 'No LICAs were deactivated.'

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, LINE_ITEM_ID)
