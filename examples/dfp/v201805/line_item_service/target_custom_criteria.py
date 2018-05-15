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

"""This example updates a line item to add custom criteria targeting.

To determine which line items exist, run get_all_line_items.py. To determine
which custom targeting keys and values exist, run
get_all_custom_targeting_keys_and_values.py.
"""


import pprint

# Import appropriate modules from the client library.
from googleads import dfp

LINE_ITEM_ID = 'INSERT_LINE_ITEM_ID_HERE'
KEY_ID1 = 'INSERT_TARGETING_KEY_ID_HERE'
KEY_ID2 = 'INSERT_TARGETING_KEY_ID_HERE'
KEY_ID3 = 'INSERT_TARGETING_KEY_ID_HERE'

VALUE_ID1 = 'INSERT_TARGETING_VALUE_ID_HERE'
VALUE_ID2 = 'INSERT_TARGETING_VALUE_ID_HERE'
VALUE_ID3 = 'INSERT_TARGETING_VALUE_ID_HERE'


def main(client, line_item_id, key_id1, key_id2, key_id3, value_id1, value_id2,
         value_id3):
  # Initialize appropriate service.
  line_item_service = client.GetService('LineItemService', version='v201805')

  # create custom criterias
  custom_criteria1 = {
      'xsi_type': 'CustomCriteria',
      'keyId': key_id1,
      'valueIds': [value_id1],
      'operator': 'IS'
  }

  custom_criteria2 = {
      'xsi_type': 'CustomCriteria',
      'keyId': key_id2,
      'valueIds': [value_id2],
      'operator': 'IS_NOT'
  }

  custom_criteria3 = {
      'xsi_type': 'CustomCriteria',
      'keyId': key_id3,
      'valueIds': [value_id3],
      'operator': 'IS'
  }

  # Create the custom criteria set that will resemble:
  # (custom_criteria1.key == custom_criteria1.value OR
  #  (custom_criteria2.key != custom_criteria2.value AND
  #   custom_criteria13.key == custom_criteria3.value))
  sub_set = {
      'xsi_type': 'CustomCriteriaSet',
      'logicalOperator': 'AND',
      'children': [custom_criteria2, custom_criteria3]
  }

  top_set = {
      'xsi_type': 'CustomCriteriaSet',
      'logicalOperator': 'OR',
      'children': [custom_criteria1, sub_set]
  }

  # Create statement to get the line item
  statement = (dfp.StatementBuilder()
               .Where('id = :lineItemId')
               .WithBindVariable('lineItemId', long(line_item_id))
               .Limit(1))

  # Set custom criteria targeting on the line item.
  line_item = line_item_service.getLineItemsByStatement(
      statement.ToStatement())['results'][0]
  line_item['targeting']['customTargeting'] = top_set

  # Update line item.
  line_item = line_item_service.updateLineItems([line_item])[0]

  # Display results.
  if line_item:
    print ('Line item with id "%s" updated with custom criteria targeting:'
           % line_item['id'])
    pprint.pprint(line_item['targeting']['customTargeting'])
  else:
    print 'No line items were updated.'


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, LINE_ITEM_ID, KEY_ID1, KEY_ID2, KEY_ID3, VALUE_ID1,
       VALUE_ID2, VALUE_ID3)
