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

"""Adds page feed to specify URLs to use with your Dynamic Search Ads campaign.

To create a Dynamic Search Ads campaign, run add_dynamic_search_ad_campaign.py.
To get campaigns, run get_campaigns.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.
"""

from collections import namedtuple
import uuid

from googleads import adwords


AD_GROUP_ID = 'INSERT_AD_GROUP_ID_HERE'
CAMPAIGN_ID = 'INSERT_CAMPAIGN_ID_HERE'

# Used to keep track of DSA page feed details.
_DSAFeedDetails = namedtuple(
    '_DSAFeedDetails', ['feed_id', 'url_attribute_id', 'label_attribute_id'])
# ID that corresponds to the labels.
DSA_LABEL_FIELD_ID = 2
# The criterion type to be used for DSA page feeds.
DSA_PAGE_FEED_CRITERION_TYPE = 61
DSA_PAGE_URL_LABEL = 'discounts'
# ID that corresponds to the page URLs.
DSA_PAGE_URLS_FIELD_ID = 1


def main(client, campaign_id, ad_group_id):
  # Get the page feed details. This code example creates a new feed, but you can
  # fetch and re-use an existing feed.
  feed_details = _CreateFeed(client)
  _CreateFeedMapping(client, feed_details)
  _CreateFeedItems(client, feed_details, DSA_PAGE_URL_LABEL)

  # Associate the page feed with the campaign.
  _UpdateCampaignDSASetting(client, campaign_id, feed_details.feed_id)

  # Optional: Target web pages matching the feed's label in the ad group.
  _AddDSATargeting(client, ad_group_id, DSA_PAGE_URL_LABEL)

  print 'Dynamic page feed setup complete for campaign ID "%d".' % campaign_id


def _CreateFeed(client):
  """Creates the feed for DSA page URLs.

  Args:
    client: an AdWordsClient instance.

  Returns:
    A _DSAFeedDetails instance containing details about the created feed.
  """
  # Get the FeedService.
  feed_service = client.GetService('FeedService', version='v201802')

  # Create operation.
  operation = {
      # Create the feed.
      'operand': {
          'name': 'DSA Feed %s' % uuid.uuid4(),
          # Create attributes.
          'attributes': [
              {'type': 'URL_LIST', 'name': 'Page URL'},
              {'type': 'STRING_LIST', 'name': 'Label'}
          ],
          'origin': 'USER'
      },
      'operator': 'ADD'
  }

  # Add the feed.
  feed = feed_service.mutate([operation])['value'][0]
  return _DSAFeedDetails(feed['id'], feed['attributes'][0]['id'],
                         feed['attributes'][1]['id'])


def _CreateFeedMapping(client, feed_details):
  """Creates the feed mapping for DSA page feeds.

  Args:
    client: an AdWordsClient instance.
    feed_details: a _DSAFeedDetails instance.
  """
  # Get the FeedMappingService.
  feed_mapping_service = client.GetService('FeedMappingService',
                                           version='v201802')

  # Create the operation.
  operation = {
      # Create the feed mapping.
      'operand': {
          'criterionType': DSA_PAGE_FEED_CRITERION_TYPE,
          'feedId': feed_details.feed_id,
          # Map the feedAttributeIds to the fieldId constants.
          'attributeFieldMappings': [
              {
                  'feedAttributeId': feed_details.url_attribute_id,
                  'fieldId': DSA_PAGE_URLS_FIELD_ID
              },
              {
                  'feedAttributeId': feed_details.label_attribute_id,
                  'fieldId': DSA_LABEL_FIELD_ID
              }
          ]
      },
      'operator': 'ADD'
  }

  # Add the feed mapping.
  feed_mapping_service.mutate([operation])


def _CreateFeedItems(client, feed_details, label_name):
  """Creates the page URLs in the DSA page feed.

  Args:
    client: an AdWordsClient instance.
    feed_details: a _DSAFeedDetails instance.
    label_name: a str containing the page feed URL label.
  """
  # Get the FeedItemService.
  feed_item_service = client.GetService('FeedItemService', version='v201802')

  # For page feed URL recommendations and rules, see:
  # https://support.google.com/adwords/answer/7166527
  urls = ('http://www.example.com/discounts/rental-cars?id={feeditem}',
          'http://www.example.com/discounts/hotel-deals?id={feeditem}',
          'http://www.example.com/discounts/flight-deals?id={feeditem}')

  # Create the operation.
  operations = [{
      # Create the feed item.
      'operand': {
          'feedId': feed_details.feed_id,
          'attributeValues': [
              {
                  'feedAttributeId': feed_details.url_attribute_id,
                  'stringValues': [url]
              },
              {
                  'feedAttributeId': feed_details.label_attribute_id,
                  'stringValues': [label_name]
              }
          ]
      },
      'operator': 'ADD'
  } for url in urls]

  # Add the feed item.
  feed_item_service.mutate(operations)


def _UpdateCampaignDSASetting(client, campaign_id, feed_id):
  """Updates the campaign DSA setting to DSA pagefeeds.

  Args:
    client: an AdWordsClient instance.
    campaign_id: a str Campaign ID.
    feed_id: a str page Feed ID.

  Raises:
    ValueError: If the given campaign is found not to be a dynamic search ad
    campaign.
  """
  # Get the CampaignService.
  campaign_service = client.GetService('CampaignService', version='v201802')

  selector = {
      'fields': ['Id', 'Settings'],
      'predicates': [{
          'field': 'Id',
          'operator': 'EQUALS',
          'values': [campaign_id]
      }]
  }

  response = campaign_service.get(selector)

  if response['totalNumEntries']:
    campaign = response['entries'][0]
  else:
    raise ValueError('No campaign with ID "%d" exists.' % campaign_id)

  if not campaign['settings']:
    raise ValueError('This is not a DSA campaign.')

  dsa_setting = None

  campaign_settings = campaign['settings']

  for setting in campaign_settings:
    if setting['Setting.Type'] == 'DynamicSearchAdsSetting':
      dsa_setting = setting
      break

  if dsa_setting is None:
    raise ValueError('This is not a DSA campaign.')

  dsa_setting['pageFeed'] = {
      'feedIds': [feed_id]
  }

  # Optional: Specify whether only the supplied URLs should be used with your
  # Dynamic Search Ads.
  dsa_setting['useSuppliedUrlsOnly'] = True

  operation = {
      'operand': {
          'id': campaign_id,
          'settings': campaign_settings
      },
      'operator': 'SET'
  }

  campaign_service.mutate([operation])
  print 'DSA page feed for campaign ID "%d" was updated with feed ID "%d".' % (
      campaign_id, feed_id)


def _AddDSATargeting(client, ad_group_id, label_name):
  """Set custom targeting for the page feed URLs based on a list of labels.

  Args:
    client: an AdWordsClient instance.
    ad_group_id: a str AdGroup ID.
    label_name: a str label name.

  Returns:
    A suds.sudsobject.Object representing the newly created webpage criterion.
  """
  # Get the AdGroupCriterionService.
  ad_group_criterion_service = client.GetService('AdGroupCriterionService',
                                                 version='v201802')

  # Create the operation.
  operation = {
      'operand': {
          'xsi_type': 'BiddableAdGroupCriterion',
          'adGroupId': ad_group_id,
          # Create a webpage criterion.
          'criterion': {
              'xsi_type': 'Webpage',
              'parameter': {
                  'criterionName': 'Test criterion',
                  # Add a condition for label=specified_label_name.
                  'conditions': [{
                      'operand': 'CUSTOM_LABEL',
                      'argument': label_name
                  }],
              }
          },
          # Set a custom bid for this criterion
          'biddingStrategyConfiguration': {
              'bids': [{
                  'xsi_type': 'CpcBid',
                  'bid': {
                      'microAmount': 1500000
                  }
              }]
          }
      },
      'operator': 'ADD'
  }

  criterion = ad_group_criterion_service.mutate([operation])['value'][0]
  print 'Web page criterion with ID "%d" and status "%s" was created.' % (
      criterion['criterion']['id'], criterion['userStatus'])
  return criterion


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()
  main(adwords_client, CAMPAIGN_ID, AD_GROUP_ID)
