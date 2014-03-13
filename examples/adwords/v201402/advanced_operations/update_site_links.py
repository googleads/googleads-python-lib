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

"""This example updates an existing sitelinks feed.

Specifically, it does the following:
  * Adds FeedItemAttributes for line 1 and line 2 descriptions to the Feed
  * Populates the new FeedItemAttributes on FeedItems in the Feed
  * Replaces the Feed's existing FeedMapping with one that contains the new
     set of FeedItemAttributes

The end result of this is that any campaign or ad group whose CampaignFeed
or AdGroupFeed points to the Feed's ID will now serve line 1 and line 2
descriptions in its sitelinks.

Tags: FeedItemService.mutate
Tags: FeedMappingService.mutate, FeedService.mutate
"""

__author__ = 'Joseph DiLallo'

from googleads import adwords

FEED_ID = 'FEED_ID'
FEED_ITEM_DESCRIPTIONS = {
    'INSERT_FEED_ITEM_A_ID_HERE': [
        'INSERT_FEED_ITEM_A_LINE1_DESC_HERE',
        'INSERT_FEED_ITEM_A_LINE2_DESC_HERE'
    ],
    'INSERT_FEED_ITEM_B_ID_HERE': [
        'INSERT_FEED_ITEM_B_LINE1_DESC_HERE',
        'INSERT_FEED_ITEM_B_LINE2_DESC_HERE'
    ]
}

# See the Placeholder reference page for a list of all the placeholder types
# and fields:
#     https://developers.google.com/adwords/api/docs/appendix/placeholders
PLACEHOLDER_FIELD_LINE_1_TEXT = 3
PLACEHOLDER_FIELD_LINE_2_TEXT = 4


def main(client, feed_id, feed_item_descriptions):
  feed_service = client.GetService('FeedService', 'v201402')
  feed_item_service = client.GetService('FeedItemService', 'v201402')
  feed_mapping_service = client.GetService('FeedMappingService', 'v201402')

  feed_selector = {
      'fields': ['Id', 'Attributes'],
      'predicates': [
          {'field': 'Id', 'operator': 'EQUALS', 'values': [feed_id]}
      ]
  }

  feed = feed_service.get(feed_selector)['entries'][0]

  # Add new line1 and line2 feed attributes.
  next_attribute_index = len(feed['attributes'])

  feed['attributes'] = [
      {'type': 'STRING', 'name': 'Line 1 Description'},
      {'type': 'STRING', 'name': 'Line 2 Description'}
  ]

  mutated_feed_result = feed_service.mutate([
      {'operator': 'SET', 'operand': feed}
  ])

  mutated_feed = mutated_feed_result['value'][0]
  line_1_attribute = mutated_feed['attributes'][next_attribute_index]
  line_2_attribute = mutated_feed['attributes'][next_attribute_index + 1]

  # Update feed items.
  feed_item_ids = feed_item_descriptions.keys()
  item_selector = {
      'fields': ['FeedId', 'FeedItemId', 'AttributeValues'],
      'predicates': [
          {'field': 'FeedId', 'operator': 'EQUALS', 'values': [feed_id]},
          {'field': 'FeedItemId', 'operator': 'IN', 'values': feed_item_ids}
      ]
  }

  feed_items = feed_item_service.get(item_selector)['entries']

  item_operations = []
  for feed_item in feed_items:
    feed_item['attributeValues'] = [
        {
            'feedAttributeId': line_1_attribute['id'],
            'stringValue': feed_item_descriptions[feed_item['feedItemId']][0]
        },
        {
            'feedAttributeId': line_2_attribute['id'],
            'stringValue': feed_item_descriptions[feed_item['feedItemId']][1]
        }
    ]

    item_operations.append({'operator': 'SET', 'operand': feed_item})

  items_update_result = feed_item_service.mutate(item_operations)
  print 'Updated %d items' % len(items_update_result['value'])

  # Update feed mapping.
  mapping_selector = {
      'fields': [
          'FeedId',
          'FeedMappingId',
          'PlaceholderType',
          'AttributeFieldMappings'
      ],
      'predicates': [
          {'field': 'FeedId', 'operator': 'EQUALS', 'values': [feed_id]}
      ]
  }
  feed_mapping_results = feed_mapping_service.get(mapping_selector)
  feed_mapping = feed_mapping_results['entries'][0]

  # Feed mappings are immutable, so we have to delete it and re-add
  # it with modifications.
  feed_mapping = feed_mapping_service.mutate([
      {'operator': 'REMOVE', 'operand': feed_mapping}
  ])['value'][0]

  feed_mapping['attributeFieldMappings'].push(
      {
          'feedAttributeId': line_1_attribute['id'],
          'fieldId': PLACEHOLDER_FIELD_LINE_1_TEXT
      },
      {
          'feedAttributeId': line_2_attribute['id'],
          'fieldId': PLACEHOLDER_FIELD_LINE_2_TEXT
      }
  )
  mapping_update_result = feed_mapping_service.mutate([
      {'operator': 'ADD', 'operand': feed_mapping}
  ])

  mutated_mapping = mapping_update_result['value'][0]
  print ('Updated field mappings for feedId %d and feedMappingId %d to:' %
         (mutated_mapping['feedId'], mutated_mapping['feedMappingId']))
  for field_mapping in mutated_mapping['attributeFieldMappings']:
    print ('\tfeedAttributeId %d --> fieldId %d' %
           (field_mapping['feedAttributeId'], field_mapping['fieldId']))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, FEED_ID, FEED_ITEM_DESCRIPTIONS)
