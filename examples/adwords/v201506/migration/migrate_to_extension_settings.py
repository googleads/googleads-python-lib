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

"""Migrates Feed-based sitelinks at Campaign level to use extension settings.

To learn more about extensionsettings, see:
https://developers.google.com/adwords/api/docs/guides/extension-settings.

To learn more about migrating Feed-based extensions to extension settings, see:
https://developers.google.com/adwords/api/docs/guides/migrate-to-extension-settings

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


from googleads import adwords


# The placeholder type for sitelinks. For the list of all supported placeholder
# types, see:
# https://developers.google.com/adwords/api/docs/appendix/placeholders
PLACEHOLDER_TYPE_SITELINKS = 1


# The placeholder field IDs for sitelinks. For the list of all supported
# placeholder types, see:
# https://developers.google.com/adwords/api/docs/appendix/placeholders
SITE_LINK_FIELDS = {
    'TEXT': 1,
    'URL': 2,
    'LINE2': 3,
    'LINE3': 4,
    'FINAL_URLS': 5,
    'FINAL_MOBILE_URLS': 6,
    'TRACKING_URL_TEMPLATE': 7
}


PAGE_SIZE = 500


def CreateExtensionSetting(client, feed_items, campaign_feed, feed_item_ids,
                           platform_restrictions=None):
  """Creates the extension setting for a list of Feed Items.

  Args:
    client: an AdWordsClient instance.
    feed_items: the list of all Feed Items.
    campaign_feed: the original Campaign Feed.
    feed_item_ids: the Ids of the feed items for which extension settings should
        be created.
    platform_restrictions: an optional Platform Restriction for the Feed items.
  """
  campaign_extension_setting_service = client.GetService(
      'CampaignExtensionSettingService', 'v201506')

  extension_feed_items = [{
      CreateSitelinkFeedItem(feed_items, feed_item_id)
  } for feed_item_id in feed_item_ids]

  extension_setting = {
      'extensions': extension_feed_items
  }

  if platform_restrictions:
    extension_setting['platformRestrictions'] = platform_restrictions

  campaign_extension_setting = {
      'campaignId': campaign_feed['campaignId'],
      'extensionType': 'SITELINK',
      'extensionSetting': extension_setting
  }

  operation = {
      'operand': campaign_extension_setting,
      'operator': 'ADD'
  }

  campaign_extension_setting_service.mutate([operation])


def CreateSitelinkFeedItem(feed_items, feed_item_id):
  """Creates a Sitelink Feed Item.

  Args:
    feed_items: a list of all Feed Items.
    feed_item_id: the Id of a specific Feed Item for which a Sitelink Feed Item
        should be created.

  Returns:
    The new Sitelink Feed Item.
  """
  site_link_from_feed = feed_items[feed_item_id]
  site_link_feed_item = {
      'sitelinkText': site_link_from_feed['text'],
      'sitelinkLine2': site_link_from_feed['line2'],
      'sitelinkLine3': site_link_from_feed['line3'],
      'scheduling': site_link_from_feed['scheduling']
  }

  if 'finalUrls' in site_link_from_feed and site_link_from_feed['finalUrls']:
    site_link_feed_item['sitelinkFinalUrls'] = {
        'urls': site_link_from_feed['finalUrls']
    }

    if 'finalMobileUrls' in site_link_from_feed:
      site_link_feed_item['sitelinkFinalMobileUrls'] = {
          'urls': site_link_from_feed['finalMobileUrls']
      }

    site_link_feed_item['sitelinkTrackingUrlTemplate'] = (
        site_link_from_feed['trackingUrlTemplate'])
  else:
    site_link_feed_item['sitelinkUrl'] = site_link_from_feed['url']

  return site_link_feed_item


def DeleteCampaignFeed(client, campaign_feed):
  """Deletes a campaign feed.

  Args:
    client: an AdWordsClient instance.
    campaign_feed: the campaign feed to delete.
  """
  campaign_feed_service = client.GetService('CampaignFeedService', 'v201506')

  operation = {
      'operand': campaign_feed,
      'operator': 'REMOVE'
  }

  campaign_feed_service.mutate([operation])


def DeleteOldFeedItems(client, feed_item_ids, feed):
  """Deletes the old feed items for which extension settings have been created.

  Args:
    client: an AdWordsClient instance.
    feed_item_ids: a list of Feed Item Ids.
    feed: the Feed containing the given Feed Item Ids.
  """
  if not feed_item_ids:
    return

  feed_item_service = client.GetService('FeedItemService', 'v201506')

  operations = [{
      'operator': 'REMOVE',
      'operand': {
          'feedId': feed['id'],
          'feedItemId': feed_item_id
      }
  } for feed_item_id in feed_item_ids]

  feed_item_service.mutate(operations)


def GetCampaignFeeds(client, feed, placeholder_type):
  """Get a list of Feed Item Ids used by a campaign via a given Campaign Feed.

  Args:
    client: an AdWordsClient instance.
    feed: a Campaign Feed.
    placeholder_type: the Placeholder Type.

  Returns:
    A list of Feed Item Ids.
  """
  campaign_feed_service = client.GetService('CampaignFeedService', 'v201506')

  campaign_feeds = []
  more_pages = True

  selector = {
      'fields': ['CampaignId', 'MatchingFunction', 'PlaceholderTypes'],
      'predicates': [
          {
              'field': 'Status',
              'operator': 'EQUALS',
              'values': ['ENABLED']
          },
          {
              'field': 'FeedId',
              'operator': 'EQUALS',
              'values': [feed['id']]
          },
          {
              'field': 'PlaceholderTypes',
              'operator': 'CONTAINS_ANY',
              'values': [placeholder_type]
          }
      ],
      'paging': {
          'startIndex': 0,
          'numberResults': PAGE_SIZE
      }
  }

  while more_pages:
    page = campaign_feed_service.get(selector)

    if 'entries' in page:
      campaign_feeds.extend(page['entries'])

    selector['paging']['startIndex'] += PAGE_SIZE
    more_pages = selector['paging']['startIndex'] < int(page['totalNumEntries'])

  return campaign_feeds


def GetFeeds(client):
  """Returns a list of all enabled Feeds.

  Args:
    client: an AdWordsClient instance.

  Returns:
    A list containing all enabled Feeds.
  """
  feed_service = client.GetService('FeedService', 'v201506')

  feeds = []
  more_pages = True

  selector = {
      'fields': ['Id', 'Name', 'Attributes'],
      'predicates': [
          {
              'field': 'Origin',
              'operator': 'EQUALS',
              'values': ['USER']
          },
          {
              'field': 'FeedStatus',
              'operator': 'EQUALS',
              'values': ['ENABLED']
          }
      ],
      'paging': {
          'startIndex': 0,
          'numberResults': PAGE_SIZE
      }
  }

  while more_pages:
    page = feed_service.get(selector)

    if 'entries' in page:
      feeds.extend(page['entries'])

    selector['paging']['startIndex'] += PAGE_SIZE
    more_pages = selector['paging']['startIndex'] < int(page['totalNumEntries'])

  return feeds


def GetFeedItems(client, feed):
  """Returns the Feed Items for a given Feed.

  Args:
    client: an AdWordsClient instance.
    feed: the Feed we are retrieving Feed Items from.

  Returns:
    The Feed Items associated with the given Feed.
  """
  feed_item_service = client.GetService('FeedItemService', 'v201506')

  feed_items = []
  more_pages = True

  selector = {
      'fields': ['FeedItemId', 'AttributeValues', 'Scheduling'],
      'predicates': [
          {
              'field': 'Status',
              'operator': 'EQUALS',
              'values': ['ENABLED']
          },
          {
              'field': 'FeedId',
              'operator': 'EQUALS',
              'values': [feed['id']]
          }
      ],
      'paging': {
          'startIndex': 0,
          'numberResults': PAGE_SIZE
      }
  }

  while more_pages:
    page = feed_item_service.get(selector)

    if 'entries' in page:
      feed_items.extend(page['entries'])

    selector['paging']['startIndex'] += PAGE_SIZE
    more_pages = selector['paging']['startIndex'] < int(page['totalNumEntries'])

  return feed_items


def GetFeedItemIdsForCampaign(campaign_feed):
  """Gets the Feed Item Ids used by a campaign through a given Campaign Feed.

  Args:
    campaign_feed: the Campaign Feed we are retrieving Feed Item Ids from.

  Returns:
    A list of Feed Item IDs.
  """
  feed_item_ids = set()

  try:
    lhs_operand = campaign_feed['matchingFunction']['lhsOperand']
  except KeyError:
    lhs_operand = None

  if (lhs_operand and lhs_operand[0]['FunctionArgumentOperand.Type'] ==
      'RequestContextOperand'):
    request_context_operand = lhs_operand[0]

    if (request_context_operand['contextType'] == 'FEED_ITEM_ID' and
        campaign_feed['matchingFunction']['operator'] == 'IN'):
      for argument in campaign_feed['matchingFunction']['rhsOperand']:
        if argument['xsi_type'] == 'ConstantOperand':
          feed_item_ids.add(argument['longValue'])

  return feed_item_ids


def GetFeedMapping(client, feed, placeholder_type):
  """Gets the Feed Mapping for a given Feed.

  Args:
    client: an AdWordsClient instance.
    feed: the Feed we are retrieving the Feed Mapping for.
    placeholder_type: the Placeholder Type we are looking for.
  Returns:
    A dictionary containing the Feed Mapping.
  """
  feed_mapping_service = client.GetService('FeedMappingService', 'v201506')

  attribute_mappings = {}
  more_pages = True

  selector = {
      'fields': ['FeedMappingId', 'AttributeFieldMappings'],
      'predicates': [
          {
              'field': 'FeedId',
              'operator': 'EQUALS',
              'values': [feed['id']]
          },
          {
              'field': 'PlaceholderType',
              'operator': 'EQUALS',
              'values': [placeholder_type]
          }
      ],
      'paging': {
          'startIndex': 0,
          'numberResults': PAGE_SIZE
      }
  }

  while more_pages:
    page = feed_mapping_service.get(selector)

    if 'entries' in page:
      # Normally, a feed attribute is mapped only to one field. However, you may
      # map it to more than one field if needed.
      for feed_mapping in page['entries']:
        for attribute_mapping in feed_mapping['attributeFieldMappings']:
          # Since attribute mappings can have multiple values for each key,
          # we use a list to store the values.
          if attribute_mapping['feedAttributeId'] in attribute_mappings:
            attribute_mappings[attribute_mapping['feedAttributeId']].append(
                attribute_mapping['fieldId'])
          else:
            attribute_mappings[attribute_mapping['feedAttributeId']] = [
                attribute_mapping['fieldId']]

    selector['paging']['startIndex'] += PAGE_SIZE
    more_pages = selector['paging']['startIndex'] < int(page['totalNumEntries'])

  return attribute_mappings


def GetPlatformRestrictions(campaign_feed):
  """Get the Platform Restrictions for a given Campaign Feed.

  Args:
    campaign_feed: the Campaign Feed we are retreiving Platform Restrictons for.

  Returns:
    The Platform Restrictions for the given feed.
  """
  platform_restrictions = None

  if campaign_feed['matchingFunction']['operator'] == 'AND':
    for argument in campaign_feed['matchingFunction']['lhsOperand']:
      # Check if matchingFunction is EQUALS(CONTEXT.DEVICE, 'Mobile')
      if argument['value']['operator'] == 'EQUALS':
        request_context_operand = argument['value']['lhsOperand'][0]

        if (request_context_operand and
            request_context_operand == 'DEVICE_PLATFORM'):
                  # This needs to be capitalized for ExtensionSettingPlatform.
          platform_restrictions = argument['value']['rhsOperand'][0].upper()

  return platform_restrictions


def GetSitelinksFromFeed(client, feed):
  """Gets the sitelinks from a feed.

  Args:
    client: an AdWordsClient instance.
    feed: the feed used to retrieve sitelinks.

  Returns:
    A dictionary mapping the feed item ID to SiteLinkFromFeed.
  """
  # Retrieve the feed's attribute mapping.
  feed_mappings = GetFeedMapping(client, feed, PLACEHOLDER_TYPE_SITELINKS)

  feed_items = {}

  for feed_item in GetFeedItems(client, feed):
    site_link_from_feed = {}

    for attribute_value in feed_item['attributeValues']:
      if attribute_value['feedAttributeId'] in feed_mappings:
        for field_id in feed_mappings[attribute_value['feedAttributeId']]:
          if field_id == SITE_LINK_FIELDS['TEXT']:
            site_link_from_feed['text'] = attribute_value['stringValue']
          elif field_id == SITE_LINK_FIELDS['URL']:
            site_link_from_feed['url'] = attribute_value['stringValue']
          elif field_id == SITE_LINK_FIELDS['FINAL_URLS']:
            site_link_from_feed['finalUrls'] = attribute_value['stringValues']
          elif field_id == SITE_LINK_FIELDS['FINAL_MOBILE_URLS']:
            site_link_from_feed['finalMobileUrls'] = attribute_value[
                'stringValues']
          elif field_id == SITE_LINK_FIELDS['TRACKING_URL_TEMPLATE']:
            site_link_from_feed['trackingUrlTemplate'] = attribute_value[
                'stringValue']
          elif field_id == SITE_LINK_FIELDS['LINE2']:
            site_link_from_feed['line2'] = attribute_value['stringValue']
          elif field_id == SITE_LINK_FIELDS['LINE3']:
            site_link_from_feed['line3'] = attribute_value['stringValue']
          else:
            print 'No applicable Site Link Field found for Id: %s' % field_id

    if 'scheduling' in feed_item:
      site_link_from_feed['scheduling'] = feed_item['scheduling']
    feed_items[feed_item['feedItemId']] = site_link_from_feed

  return feed_items


def main(client):
  # Get all of the feeds for the current user.
  feeds = GetFeeds(client)

  for feed in feeds:
    # Retrieve all the sitelinks from the current feed.
    feed_items = GetSitelinksFromFeed(client, feed)

    # Get all the instances where a sitelink from this feed has been added to a
    # campaign.
    campaign_feeds = GetCampaignFeeds(client, feed, PLACEHOLDER_TYPE_SITELINKS)

    all_feed_items_to_delete = []
    for campaign_feed in campaign_feeds:
      # Retrieve the sitelinks that have been associated with this Campaign.
      feed_item_ids = GetFeedItemIdsForCampaign(campaign_feed)

      if feed_item_ids == 0:
        print ('Migration skipped for campaign feed with campaign ID %d '
               'and feed ID %d because no mapped feed item IDs were found in '
               'the campaign feed\'s matching function.'
               % (campaign_feed['campaign_id'], campaign_feed['feed_id']))
        continue

      platform_restrictions = GetPlatformRestrictions(campaign_feed)

      # Delete the campaign feed that associates the sitelinks from the feed to
      # the Campaign.
      DeleteCampaignFeed(client, campaign_feed)

      # Create extension settings instead of sitelinks.
      CreateExtensionSetting(client, feed_items, campaign_feed, feed_item_ids,
                             platform_restrictions)

      # Mark the sitelinks from the feed for deletion.
      all_feed_items_to_delete.extend(feed_item_ids)

    # Delete all the sitelinks from the feed.
    DeleteOldFeedItems(client, all_feed_items_to_delete, feed)


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client)
