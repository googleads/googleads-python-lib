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

"""This code example creates a new line item to serve to video content.

This feature is only available to Ad Manager 360 solution networks.
"""

import datetime
import uuid

# Import appropriate modules from the client library.
from googleads import ad_manager
import pytz

# Set order that all created line item will belong to and the video ad unit id
# to target.
ORDER_ID = 'INSERT_ORDER_ID_HERE'
TARGETED_VIDEO_AD_UNIT_ID = 'INSERT_TARGETED_VIDEO_AD_UNIT_ID_HERE'

# Set the video content to target.
CONTENT_ID = 'INSERT_CONTENT_ID_HERE'
# Set the video content bundle to target.
CONTENT_BUNDLE_ID = 'INSERT_CONTENT_BUNDLE_ID_HERE'
# Set the CMS metadata value to target.
CMS_METADATA_VALUE_ID = 'INSERT_CMS_METADATA_VALUE_ID_HERE'


def main(client, order_id, targeted_video_ad_unit_id, content_id,
         content_bundle_id, cms_metadata_value_id):
  # Initialize appropriate service.
  line_item_service = client.GetService('LineItemService', version='v201911')

  end_datetime = datetime.datetime.now(tz=pytz.timezone('America/New_York'))
  end_datetime += datetime.timedelta(days=365)

  # Create line item object.
  line_item = {
      'name': 'Line item #%s' % uuid.uuid4(),
      'orderId': order_id,
      'targeting': {
          'contentTargeting': {
              'targetedContentIds': [content_id],
              'targetedVideoContentBundleIds': [content_bundle_id]
          },
          'customTargeting': {
              'logicalOperator': 'AND',
              'children': [{
                  'xsi_type': 'CmsMetadataCriteria',
                  'cmsMetadataValueIds': [cms_metadata_value_id],
                  'operator': 'EQUALS'
              }]
          },
          'inventoryTargeting': {
              'targetedAdUnits': [{
                  'adUnitId': targeted_video_ad_unit_id,
                  'includeDescendants': 'true'
              }]
          },
          'requestPlatformTargeting': {
              'targetedRequestPlatforms': ['VIDEO_PLAYER']
          },
          'videoPositionTargeting': {
              'targetedPositions': [{
                  'videoPosition': {
                      'positionType': 'PREROLL'
                  }
              }]
          }
      },
      'creativePlaceholders': [{
          'size': {
              'width': '400',
              'height': '300'
          },
          'companions': [{
              'size': {
                  'width': '300',
                  'height': '250'
              },
          }, {
              'size': {
                  'width': '728',
                  'height': '90'
              },
          }]
      }],
      'environmentType': 'VIDEO_PLAYER',
      'companionDeliveryOption': 'OPTIONAL',
      'startDateTimeType': 'IMMEDIATELY',
      'lineItemType': 'SPONSORSHIP',
      'endDateTime': end_datetime,
      'costType': 'CPM',
      'costPerUnit': {
          'currencyCode': 'USD',
          'microAmount': '2000000'
      },
      'primaryGoal': {
          'units': '50',
          'unitType': 'IMPRESSIONS',
          'goalType': 'DAILY'
      },
      'contractedUnitsBought': '100',
      'creativeRotationType': 'OPTIMIZED',
      'discountType': 'PERCENTAGE',
      'allowOverbook': 'true'
  }

  # Add line item.
  line_item = line_item_service.createLineItems([line_item])[0]

  # Display results.
  print('Video line item with id "%s", belonging to order id "%s", and '
        'named "%s" was created.' % (line_item['id'], line_item['orderId'],
                                     line_item['name']))

if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, ORDER_ID, TARGETED_VIDEO_AD_UNIT_ID, CONTENT_ID,
       CONTENT_BUNDLE_ID, CMS_METADATA_VALUE_ID)
