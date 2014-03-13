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

"""This example adds a sitelinks feed and associates it with a campaign.

Tags: CampaignFeedService.mutate, FeedItemService.mutate
Tags: FeedMappingService.mutate, FeedService.mutate
Api: AdWordsOnly
"""

__author__ = 'Joseph DiLallo'

from googleads import adwords
from googleads import errors

# See the Placeholder reference page for a list of all the placeholder types and
# fields.
# https://developers.google.com/adwords/api/docs/appendix/placeholders.html
PLACEHOLDER_SITELINKS = '1'
PLACEHOLDER_FIELD_SITELINK_LINK_TEXT = '1'
PLACEHOLDER_FIELD_SITELINK_LINK_URL = '2'
PLACEHOLDER_FIELD_LINE_1_TEXT = '3'
PLACEHOLDER_FIELD_LINE_2_TEXT = '4'

CAMPAIGN_ID = 'INSERT_CAMPAIGN_ID_HERE'


def main(client, campaign_id):
  # Initialize appropriate service.
  feed_service = client.GetService('FeedService', version='v201402')
  feed_item_service = client.GetService('FeedItemService', version='v201402')
  feed_mapping_service = client.GetService(
      'FeedMappingService', version='v201402')
  campaign_feed_service = client.GetService(
      'CampaignFeedService', version='v201402')

  sitelinks_data = {}

  # Create site links feed first.
  site_links_feed = {
      'name': 'Feed For Site Links',
      'attributes': [
          {'type': 'STRING', 'name': 'Link Text'},
          {'type': 'URL', 'name': 'Link URL'},
          {'type': 'STRING', 'name': 'Line 1 Description'},
          {'type': 'STRING', 'name': 'Line 2 Description'}
      ]
  }

  response = feed_service.mutate([
      {'operator': 'ADD', 'operand': site_links_feed}
  ])
  if 'value' in response:
    feed = response['value'][0]
    link_text_feed_attribute_id = feed['attributes'][0]['id']
    link_url_feed_attribute_id = feed['attributes'][1]['id']
    line_1_feed_attribute_id = feed['attributes'][2]['id']
    line_2_feed_attribute_id = feed['attributes'][3]['id']
    print ('Feed with name \'%s\' and ID \'%s\' was added with' %
           (feed['name'], feed['id']))
    print ('\tText attribute ID \'%s\' and URL attribute ID \'%s\'.' %
           (link_text_feed_attribute_id, link_url_feed_attribute_id))
    print ('\tLine 1 attribute ID \'%s\' and Line 2 attribute ID \'%s\'.' %
           (line_1_feed_attribute_id, line_2_feed_attribute_id))
    sitelinks_data['feedId'] = feed['id']
    sitelinks_data['linkTextFeedId'] = link_text_feed_attribute_id
    sitelinks_data['linkUrlFeedId'] = link_url_feed_attribute_id
    sitelinks_data['line1FeedId'] = line_1_feed_attribute_id
    sitelinks_data['line2FeedId'] = line_2_feed_attribute_id
  else:
    raise errors.GoogleAdsError('No feeds were added.')

  # Create site links feed items.
  items_data = [
      {'text': 'Home', 'url': 'http://www.example.com',
       'line1': 'Home line 1', 'line2': 'Home line 2'},
      {'text': 'Stores', 'url': 'http://www.example.com/stores',
       'line1': 'Stores line 1', 'line2': 'Stores line 2'},
      {'text': 'On Sale', 'url': 'http://www.example.com/sale',
       'line1': 'On Sale line 1', 'line2': 'On Sale line 2'},
      {'text': 'Support', 'url': 'http://www.example.com/support',
       'line1': 'Support line 1', 'line2': 'Support line 2'},
      {'text': 'Products', 'url': 'http://www.example.com/products',
       'line1': 'Products line 1', 'line2': 'Products line 2'},
      {'text': 'About', 'url': 'http://www.example.com/about',
       'line1': 'About line 1', 'line2': 'About line 2'}
  ]

  feed_items = []
  for item in items_data:
    feed_items.append({
        'feedId': sitelinks_data['feedId'],
        'attributeValues': [
            {
                'feedAttributeId': sitelinks_data['linkTextFeedId'],
                'stringValue': item['text']
            },
            {
                'feedAttributeId': sitelinks_data['linkUrlFeedId'],
                'stringValue': item['url']
            },
            {
                'feedAttributeId': sitelinks_data['line1FeedId'],
                'stringValue': item['line1']
            },
            {
                'feedAttributeId': sitelinks_data['line2FeedId'],
                'stringValue': item['line2']
            }
        ],
        # Optional: use the 'startTime' and 'endTime' keys to specify the time
        # period for the feed to deliver.  The example below will make the feed
        # start now and stop in one month.
        # Make sure you specify the datetime in the customer's time zone. You
        # can retrieve this from customer['dateTimeZone'].
        #
        # ['startTime']: datetime.datetime.now().strftime('%Y%m%d %H%M%S')
        # ['endTime']: (datetime.datetime.now() +
        #               relativedelta(months=1)).strftime('%Y%m%d %H%M%S')

        # Optional: use the 'scheduling' key to specify time and days of the
        # week for feed to deliver. This is a Beta feature.
    })

  feed_items_operations = [{'operator': 'ADD', 'operand': item} for item
                           in feed_items]

  response = feed_item_service.mutate(feed_items_operations)
  if 'value' in response:
    sitelinks_data['feedItemIds'] = []
    for feed_item in response['value']:
      print 'Feed item with ID %s was added.' % feed_item['feedItemId']
      sitelinks_data['feedItemIds'].append(feed_item['feedItemId'])
  else:
    raise errors.GoogleAdsError('No feed items were added.')

  # Create site links feed mapping.

  feed_mapping = {
      'placeholderType': PLACEHOLDER_SITELINKS,
      'feedId': sitelinks_data['feedId'],
      'attributeFieldMappings': [
          {
              'feedAttributeId': sitelinks_data['linkTextFeedId'],
              'fieldId': PLACEHOLDER_FIELD_SITELINK_LINK_TEXT
          },
          {
              'feedAttributeId': sitelinks_data['linkUrlFeedId'],
              'fieldId': PLACEHOLDER_FIELD_SITELINK_LINK_URL
          },
          {
              'feedAttributeId': sitelinks_data['line1FeedId'],
              'fieldId': PLACEHOLDER_FIELD_LINE_1_TEXT
          },
          {
              'feedAttributeId': sitelinks_data['line2FeedId'],
              'fieldId': PLACEHOLDER_FIELD_LINE_2_TEXT
          }
      ]
  }

  response = feed_mapping_service.mutate([
      {'operator': 'ADD', 'operand': feed_mapping}
  ])
  if 'value' in response:
    feed_mapping = response['value'][0]
    print ('Feed mapping with ID %s and placeholder type %s was saved for feed'
           ' with ID %s.' %
           (feed_mapping['feedMappingId'], feed_mapping['placeholderType'],
            feed_mapping['feedId']))
  else:
    raise errors.GoogleAdsError('No feed mappings were added.')

  # Create site links campaign feed.
  operands = []
  for feed_item_id in sitelinks_data['feedItemIds']:
    operands.append({
        'xsi_type': 'ConstantOperand',
        'type': 'LONG',
        'longValue': feed_item_id
    })

  feed_item_function = {
      'operator': 'IN',
      'lhsOperand': [
          {'xsi_type': 'RequestContextOperand', 'contextType': 'FEED_ITEM_ID'}
      ],
      'rhsOperand': operands
  }

  # Optional: to target to a platform, define a function and 'AND' it with the
  #           feed item ID link:
  platform_function = {
      'operator': 'EQUALS',
      'lhsOperand': [
          {
              'xsi_type': 'RequestContextOperand',
              'contextType': 'DEVICE_PLATFORM'
          }
      ],
      'rhsOperand': [
          {
              'xsi_type': 'ConstantOperand',
              'type': 'STRING',
              'stringValue': 'Mobile'
          }
      ]
  }
  combined_function = {
      'operator': 'AND',
      'lhsOperand': [
          {'xsi_type': 'FunctionOperand', 'value': feed_item_function},
          {'xsi_type': 'FunctionOperand', 'value': platform_function}
      ]
  }

  campaign_feed = {
      'feedId': sitelinks_data['feedId'],
      'campaignId': campaign_id,
      'matchingFunction': combined_function,
      # Specifying placeholder types on the CampaignFeed allows the same feed
      # to be used for different placeholders in different Campaigns.
      'placeholderTypes': [PLACEHOLDER_SITELINKS]
  }

  response = campaign_feed_service.mutate([
      {'operator': 'ADD', 'operand': campaign_feed}
  ])
  if 'value' in response:
    campaign_feed = response['value'][0]
    print ('Campaign with ID %s was associated with feed with ID %s.' %
           (campaign_feed['campaignId'], campaign_feed['feedId']))
  else:
    raise errors.GoogleAdsError('No campaign feeds were added.')


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, CAMPAIGN_ID)
