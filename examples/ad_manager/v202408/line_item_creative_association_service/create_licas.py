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

"""This code example creates new line item creative associations (LICAs) for an
existing line item and a set of creative ids.

To determine which LICAs exist, run get_all_licas.py.
"""


# Import appropriate modules from the client library.
from googleads import ad_manager

# Set the line item ID and creative IDs to associate.
LINE_ITEM_ID = 'INSERT_LINE_ITEM_ID_HERE'
CREATIVE_IDS = ['INSERT_CREATIVE_IDS_HERE']


def main(client, line_item_id, creative_ids):
  # Initialize appropriate service.
  lica_service = client.GetService(
      'LineItemCreativeAssociationService', version='v202408')

  licas = []
  for creative_id in creative_ids:
    licas.append({'creativeId': creative_id,
                  'lineItemId': line_item_id})

  # Create the LICAs remotely.
  licas = lica_service.createLineItemCreativeAssociations(licas)

  # Display results.
  if licas:
    for lica in licas:
      print('LICA with line item id "%s", creative id "%s", and '
            'status "%s" was created.' %
            (lica['lineItemId'], lica['creativeId'], lica['status']))
  else:
    print('No LICAs created.')

if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, LINE_ITEM_ID, CREATIVE_IDS)
