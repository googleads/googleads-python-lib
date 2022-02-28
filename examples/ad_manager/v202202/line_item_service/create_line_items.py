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

"""This code example creates new line items.

To determine which line items exist, run get_all_line_items.py. To determine
which orders exist, run get_all_orders.py. To determine which placements exist,
run get_all_placements.py.
"""


import datetime
import uuid

# Import appropriate modules from the client library.
from googleads import ad_manager
import pytz

# Set order that the created line item will belong to and add the id of a
# placement containing ad units to target.
ORDER_ID = 'INSERT_ORDER_ID_HERE'
TARGETED_PLACEMENT_IDS = ['INSERT_PLACEMENT_IDS_HERE']


def main(client, order_id, targeted_placement_ids):
  # Initialize appropriate service.
  line_item_service = client.GetService('LineItemService', version='v202202')

  end_datetime = datetime.datetime.now(tz=pytz.timezone('America/New_York'))
  end_datetime += datetime.timedelta(days=365)

  # Create line item objects.
  line_items = []
  for _ in range(5):
    line_item = {
        'name': 'Line item #%s' % uuid.uuid4(),
        'orderId': order_id,
        'targeting': {
            'inventoryTargeting': {
                'targetedPlacementIds': targeted_placement_ids
            },
            'geoTargeting': {
                'targetedLocations': [
                    {
                        'id': '2840',
                        'displayName': 'US'
                    },
                    {
                        'id': '20133',
                        'displayName': 'Geneva'
                    },
                    {
                        'id': '9000093',
                        'displayName': 'B3P',
                    }
                ],
                'excludedLocations': [
                    {
                        'id': '1016367',
                        'displayName': 'Chicago',
                    },
                    {
                        'id': '200501',
                        'displayName': 'New York NY'
                    }
                ]
            },
            'dayPartTargeting': {
                'dayParts': [
                    {
                        'dayOfWeek': 'SATURDAY',
                        'startTime': {
                            'hour': '0',
                            'minute': 'ZERO'
                        },
                        'endTime': {
                            'hour': '24',
                            'minute': 'ZERO'
                        }
                    },
                    {
                        'dayOfWeek': 'SUNDAY',
                        'startTime': {
                            'hour': '0',
                            'minute': 'ZERO'
                        },
                        'endTime': {
                            'hour': '24',
                            'minute': 'ZERO'
                        }
                    }
                ],
                'timeZone': 'BROWSER'
            },
            'userDomainTargeting': {
                'domains': ['usa.gov'],
                'targeted': 'false'
            },
            'technologyTargeting': {
                'browserTargeting': {
                    'browsers': [{'id': '500072'}],
                    'isTargeted': 'true'
                }
            }
        },
        'creativePlaceholders': [
            {
                'size': {
                    'width': '300',
                    'height': '250'
                }
            },
            {
                'size': {
                    'width': '120',
                    'height': '600'
                }
            }
        ],
        'startDateTimeType': 'IMMEDIATELY',
        'lineItemType': 'STANDARD',
        'endDateTime': end_datetime,
        'costType': 'CPM',
        'costPerUnit': {
            'currencyCode': 'USD',
            'microAmount': '2000000'
        },
        'primaryGoal': {
            'units': '50',
            'unitType': 'IMPRESSIONS',
            'goalType': 'LIFETIME'
        },
        'contractedUnitsBought': '100',
        'creativeRotationType': 'EVEN',
        'discountType': 'PERCENTAGE',
        'allowOverbook': 'true'
    }
    line_items.append(line_item)

  # Add line items.
  line_items = line_item_service.createLineItems(line_items)

  # Display results.
  for line_item in line_items:
    print('Line item with id "%s", belonging to order id "%s", and named '
          '"%s" was created.' % (line_item['id'], line_item['orderId'],
                                 line_item['name']))

if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, ORDER_ID, TARGETED_PLACEMENT_IDS)
