#!/usr/bin/env python
#
# Copyright 2016 Google Inc. All Rights Reserved.
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

To add sitelinks using the simpler ExtensionSetting services, see:
add_sitelinks.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


import re
import uuid
from googleads import adwords
from googleads import errors

# See the Placeholder reference page for a list of all the placeholder types and
# fields.
# https://developers.google.com/adwords/api/docs/appendix/placeholders.html
PLACEHOLDER_SITELINKS = '1'
PLACEHOLDER_FIELD_SITELINK_LINK_TEXT = '1'
PLACEHOLDER_FIELD_SITELINK_FINAL_URLS = '5'
PLACEHOLDER_FIELD_LINE_2_TEXT = '3'
PLACEHOLDER_FIELD_LINE_3_TEXT = '4'

CAMPAIGN_ID = 'INSERT_CAMPAIGN_ID_HERE'
# Optional: Ad group to restrict targeting to.
AD_GROUP_ID = 'INSERT_AD_GROUP_ID_HERE'


def RestrictFeedItemToGeoTarget(client, feed_item, location_id):
  """Restrict a feed item to a geo target location.

  Args:
    client: An AdWordsClient instance.
    feed_item: A FeedItem.
    location_id: The Id of the location to restrict to.
  """
  # Retrieve the FeedItemTargetService
  feed_item_target_service = client.GetService(
      'FeedItemTargetService', version='v201809')

  # Optional: Restrict the first feed item to only serve with ads for the
  # specified geo target.
  criterion_target = {
      'xsi_type': 'FeedItemCriterionTarget',
      'feedId': feed_item['feedId'],
      'feedItemId': feed_item['feedItemId'],
      # These IDs can be found in the documentation or retrieved with the
      # LocationCriterionService.
      'criterion': {
          'xsi_type': 'Location',
          'id': location_id
      }
  }

  operation = {'operator': 'ADD', 'operand': criterion_target}

  response = feed_item_target_service.mutate([operation])
  new_location_target = response['value'][0]
  print('Feed item target for feed ID %d and feed item ID %d was created to '
        'restrict serving to location ID %d.' %
        (new_location_target['feedId'],
         new_location_target['feedItemId'],
         new_location_target['criterion']['id']))


def main(client, campaign_id, ad_group_id=None):
  # Initialize appropriate service.
  feed_service = client.GetService('FeedService', version='v201809')
  feed_item_service = client.GetService('FeedItemService', version='v201809')
  feed_item_target_service = client.GetService('FeedItemTargetService',
                                               version='v201809')
  feed_mapping_service = client.GetService(
      'FeedMappingService', version='v201809')
  campaign_feed_service = client.GetService(
      'CampaignFeedService', version='v201809')

  sitelinks_data = {}

  # Create site links feed first.
  site_links_feed = {
      'name': 'Feed For Site Links #%s' % uuid.uuid4(),
      'attributes': [
          {'type': 'STRING', 'name': 'Link Text'},
          {'type': 'URL_LIST', 'name': 'Link Final URLs'},
          {'type': 'STRING', 'name': 'Line 2 Description'},
          {'type': 'STRING', 'name': 'Line 3 Description'}
      ]
  }

  response = feed_service.mutate([
      {'operator': 'ADD', 'operand': site_links_feed}
  ])

  if 'value' in response:
    feed = response['value'][0]
    link_text_feed_attribute_id = feed['attributes'][0]['id']
    final_url_feed_attribute_id = feed['attributes'][1]['id']
    line_2_feed_attribute_id = feed['attributes'][2]['id']
    line_3_feed_attribute_id = feed['attributes'][3]['id']
    print('Feed with name "%s" and ID "%d" was added with' %
          (feed['name'], feed['id']))
    print('\tText attribute ID "%d" and Final URL attribute ID "%d".' %
          (link_text_feed_attribute_id, final_url_feed_attribute_id))
    print('\tLine 2 attribute ID "%d" and Line 3 attribute ID "%d".' %
          (line_2_feed_attribute_id, line_3_feed_attribute_id))
    sitelinks_data['feedId'] = feed['id']
    sitelinks_data['linkTextFeedId'] = link_text_feed_attribute_id
    sitelinks_data['finalUrlFeedId'] = final_url_feed_attribute_id
    sitelinks_data['line2FeedId'] = line_2_feed_attribute_id
    sitelinks_data['line3FeedId'] = line_3_feed_attribute_id
  else:
    raise errors.GoogleAdsError('No feeds were added.')

  # Create site links feed items.
  items_data = [
      {'text': 'Home', 'finalUrls': 'http://www.example.com',
       'line2': 'Home line 2', 'line3': 'Home line 3'},
      {'text': 'Stores', 'finalUrls': 'http://www.example.com/stores',
       'line2': 'Stores line 2', 'line3': 'Stores line 3'},
      {'text': 'On Sale', 'finalUrls': 'http://www.example.com/sale',
       'line2': 'On Sale line 2', 'line3': 'On Sale line 3'},
      {'text': 'Support', 'finalUrls': 'http://www.example.com/support',
       'line2': 'Support line 2', 'line3': 'Support line 3'},
      {'text': 'Products', 'finalUrls': 'http://www.example.com/products',
       'line2': 'Products line 2', 'line3': 'Products line 3'},
      {'text': 'About Us', 'finalUrls': 'http://www.example.com/about',
       'line2': 'About line 2', 'line3': 'About line 3', 'locationTarget': True}
  ]

  feed_items = []
  for item in items_data:
    feed_item = {
        'feedId': sitelinks_data['feedId'],
        'attributeValues': [
            {
                'feedAttributeId': sitelinks_data['linkTextFeedId'],
                'stringValue': item['text']
            },
            {
                'feedAttributeId': sitelinks_data['finalUrlFeedId'],
                'stringValues': [item['finalUrls']]
            },
            {
                'feedAttributeId': sitelinks_data['line2FeedId'],
                'stringValue': item['line2']
            },
            {
                'feedAttributeId': sitelinks_data['line3FeedId'],
                'stringValue': item['line3']
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
    }

    # Optional: Restrict targeting only to people physically within
    # the location.
    if 'locationTarget' in item:
      item['geoTargetingRestriction'] = {
          'geoRestriction': 'LOCATION_OF_PRESENCE'
      }

    feed_items.append(feed_item)

  feed_items_operations = [{'operator': 'ADD', 'operand': item} for item
                           in feed_items]

  response = feed_item_service.mutate(feed_items_operations)
  if 'value' in response:
    sitelinks_data['feedItemIds'] = []
    for feed_item in response['value']:
      print('Feed item with ID %d was added.' % feed_item['feedItemId'])
      sitelinks_data['feedItemIds'].append(feed_item['feedItemId'])
  else:
    raise errors.GoogleAdsError('No feed items were added.')

  # Target the "aboutUs" sitelink to geographically target California.
  # See https://developers.google.com/adwords/api/docs/appendix/geotargeting for
  # location criteria for supported locations.
  RestrictFeedItemToGeoTarget(client, response['value'][5], 21137)

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
              'feedAttributeId': sitelinks_data['finalUrlFeedId'],
              'fieldId': PLACEHOLDER_FIELD_SITELINK_FINAL_URLS
          },
          {
              'feedAttributeId': sitelinks_data['line2FeedId'],
              'fieldId': PLACEHOLDER_FIELD_LINE_2_TEXT
          },
          {
              'feedAttributeId': sitelinks_data['line3FeedId'],
              'fieldId': PLACEHOLDER_FIELD_LINE_3_TEXT
          }
      ]
  }

  response = feed_mapping_service.mutate([
      {'operator': 'ADD', 'operand': feed_mapping}
  ])
  if 'value' in response:
    feed_mapping = response['value'][0]
    print('Feed mapping with ID %d and placeholder type %s was saved for feed'
          ' with ID %d.' %
          (feed_mapping['feedMappingId'], feed_mapping['placeholderType'],
           feed_mapping['feedId']))
  else:
    raise errors.GoogleAdsError('No feed mappings were added.')

  # Construct a matching function that associates the sitelink feeditems to the
  # campaign, and set the device preference to Mobile. For more details, see the
  # matching function guide:
  # https://developers.google.com/adwords/api/docs/guides/feed-matching-functions
  matching_function_string = (
      'AND(IN(FEED_ITEM_ID, {%s}), EQUALS(CONTEXT.DEVICE, \'Mobile\'))' %
      re.sub(r'\[|\]|L', '', str(sitelinks_data['feedItemIds'])))

  campaign_feed = {
      'feedId': sitelinks_data['feedId'],
      'campaignId': campaign_id,
      'matchingFunction': {'functionString': matching_function_string},
      # Specifying placeholder types on the CampaignFeed allows the same feed
      # to be used for different placeholders in different Campaigns.
      'placeholderTypes': [PLACEHOLDER_SITELINKS]
  }

  response = campaign_feed_service.mutate([
      {'operator': 'ADD', 'operand': campaign_feed}
  ])
  if 'value' in response:
    campaign_feed = response['value'][0]
    print('Campaign with ID %d was associated with feed with ID %d.' %
          (campaign_feed['campaignId'], campaign_feed['feedId']))
  else:
    raise errors.GoogleAdsError('No campaign feeds were added.')

  # Optional: Restrict the first feed item to only serve with ads for the
  # specified ad group ID.
  if ad_group_id:
    feed_item_target = {
        'xsi_type': 'FeedItemAdGroupTarget',
        'feedId': sitelinks_data['feedId'],
        'feedItemId': sitelinks_data['feedItemIds'][0],
        'adGroupId': ad_group_id
    }

    operations = [{
        'operator': 'ADD',
        'operand': feed_item_target
    }]

    response = feed_item_target_service.mutate(operations)

    if 'value' in response:
      print('Feed item target for feed ID "%d" and feed item ID "%d" was '
            'created to restrict serving to ad group ID "%d".'
            % (feed_item_target['feedId'], feed_item_target['feedItemId'],
                feed_item_target['adGroupId']))

if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  if AD_GROUP_ID == 'INSERT_AD_GROUP_ID_HERE':
    main(adwords_client, CAMPAIGN_ID)
  else:
    main(adwords_client, CAMPAIGN_ID, ad_group_id=AD_GROUP_ID)
