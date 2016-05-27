#!/usr/bin/python
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

"""Adds an ad customizer feed.

Associates the feed with customer and adds an ad that uses the feed to populate
dynamic data.

"""


from datetime import datetime
from uuid import uuid4

# Import appropriate classes from the client library.
from googleads import adwords
from googleads import errors


FEED_NAME = 'Interplanetary Feed Name %s' % uuid4()
ADGROUPS = [
    'INSERT_ADGROUP_ID_1_HERE',
    'INSERT_ADGROUP_ID_2_HERE'
]


def CreateAdsWithCustomizations(client, adgroup_ids, feed_name):
  """Creates TextAds that use ad customizations for the specified AdGroups.

  Args:
    client: an AdWordsClient instance.
    adgroup_ids: a list containing the AdGroup ids to add TextAds to.
    feed_name: the name of the feed used to apply customizations.

  Raises:
    GoogleAdsError: if no TextAds were added.
  """
  # Get the AdGroupAdService
  adgroup_ad_service = client.GetService('AdGroupAdService')

  text_ad = {
      'xsi_type': 'TextAd',
      'headline': 'Luxury Cruise to {=%s.Name}' % feed_name,
      'description1': 'Only {=%s.Price}' % feed_name,
      'description2': 'Offer ends in {=countdown(%s.Date)}!' % feed_name,
      'finalUrls': ['http://www.example.com'],
      'displayUrl': 'www.example.com'
  }

  # We add the same ad to both ad groups. When they serve, they will show
  # different values, since they match different feed items.
  operations = [{
      'operator': 'ADD',
      'operand': {
          'adGroupId': adgroup,
          'ad': text_ad
      }
  } for adgroup in adgroup_ids]

  response = adgroup_ad_service.mutate(operations)

  if response and 'value' in response:
    for ad in response['value']:
      print ('Created an ad with ID \'%s\', type \'%s\', and status \'%s\'.'
             % (ad['ad']['id'], ad['ad']['Ad.Type'], ad['status']))
  else:
    raise errors.GoogleAdsError('No ads were added.')


def CreateCustomizerFeed(client, feed_name):
  """Creates a new AdCustomizerFeed.

  Args:
    client: an AdWordsClient instance.
    feed_name: the name for the new AdCustomizerFeed.

  Returns:
    The new AdCustomizerFeed.
  """
  # Get the AdCustomizerFeedService
  ad_customizer_feed_service = client.GetService('AdCustomizerFeedService')

  customizer_feed = {
      'feedName': feed_name,
      'feedAttributes': [
          {'type': 'STRING', 'name': 'Name'},
          {'type': 'STRING', 'name': 'Price'},
          {'type': 'DATE_TIME', 'name': 'Date'}
      ]
  }

  feed_service_operation = {
      'operator': 'ADD',
      'operand': customizer_feed
  }

  response = ad_customizer_feed_service.mutate([feed_service_operation])

  if response and 'value' in response:
    feed = response['value'][0]
    feed_data = {
        'feedId': feed['feedId'],
        'nameId': feed['feedAttributes'][0]['id'],
        'priceId': feed['feedAttributes'][1]['id'],
        'dateId': feed['feedAttributes'][2]['id']
    }
    print ('Feed with name \'%s\' and ID %s was added with:\n'
           '\tName attribute ID %s and price attribute ID %s and date attribute'
           'ID %s') % (feed['feedName'], feed['feedId'], feed_data['nameId'],
                       feed_data['priceId'], feed_data['dateId'])
    return feed
  else:
    raise errors.GoogleAdsError('No feeds were added')


def CreateCustomizerFeedItems(client, adgroup_ids, ad_customizer_feed):
  """Creates FeedItems for the specified AdGroups.

  These FeedItems contain values to use in ad customizations for the AdGroups.

  Args:
    client: an AdWordsClient instance.
    adgroup_ids: a list containing two AdGroup Ids.
    ad_customizer_feed: the AdCustomizerFeed we're associating the FeedItems
        with.

  Raises:
    GoogleAdsError: if no FeedItems were added.
  """
  # Get the FeedItemService
  feed_item_service = client.GetService('FeedItemService')
  now = datetime.now()
  mars_date = datetime(now.year, now.month, 1, 0, 0)
  venus_date = datetime(now.year, now.month, 15, 0, 0)
  time_format = '%Y%m%d %H%M%S'

  feed_item_operations = [
      CreateFeedItemAddOperation(
          'Mars', '$1234.56', mars_date.strftime(time_format), adgroup_ids[0],
          ad_customizer_feed),
      CreateFeedItemAddOperation(
          'Venus', '$1450.00', venus_date.strftime(time_format),
          adgroup_ids[1], ad_customizer_feed)
  ]

  response = feed_item_service.mutate(feed_item_operations)

  if 'value' in response:
    for feed_item in response['value']:
      print 'Added FeedItem with ID %d.' % feed_item['feedItemId']
  else:
    raise errors.GoogleAdsError('No FeedItems were added.')


def CreateFeedItemAddOperation(name, price, date, adgroup_id,
                               ad_customizer_feed):
  """Creates a FeedItemOperation.

  The generated FeedItemOperation will create a FeedItem with the specified
  values and AdGroupTargeting when sent to FeedItemService.mutate.

  Args:
    name: the value for the name attribute of the FeedItem.
    price: the value for the price attribute of the FeedItem.
    date: the value for the date attribute of the FeedItem.
    adgroup_id: the ID of the ad_group to target with the FeedItem.
    ad_customizer_feed: the AdCustomizerFeed we're associating the FeedItems
        with.

  Returns:
    A new FeedItemOperation for adding a FeedItem.
  """
  feed_item = {
      'feedId': ad_customizer_feed['feedId'],
      'adGroupTargeting': {
          'TargetingAdGroupId': adgroup_id
      },
      'attributeValues': [
          {
              'feedAttributeId': ad_customizer_feed['feedAttributes'][0]['id'],
              'stringValue': name
          },
          {
              'feedAttributeId': ad_customizer_feed['feedAttributes'][1]['id'],
              'stringValue': price
          },
          {
              'feedAttributeId': ad_customizer_feed['feedAttributes'][2]['id'],
              'stringValue': date
          }
      ]
  }

  return {'operator': 'ADD', 'operand': feed_item}


def main(client, adgroup_ids, feed_name=FEED_NAME):
  # Create a customizer feed. One feed per account can be used for all ads.
  ad_customizer_feed = CreateCustomizerFeed(client, feed_name)
  # Add feed items containing the values we'd like to place in ads.
  CreateCustomizerFeedItems(client, adgroup_ids, ad_customizer_feed)
  # All set! We can now create ads with customizations.
  CreateAdsWithCustomizations(client, adgroup_ids, feed_name)


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()
  main(adwords_client, ADGROUPS)
