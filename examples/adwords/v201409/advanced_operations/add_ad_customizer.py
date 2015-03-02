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

"""Adds an ad customizer feed.

Associates the feed with customer and adds an ad that
uses the feed to populate dynamic data.

Tags: CustomerFeedService.mutate, FeedItemService.mutate
Tags: FeedMappingService.mutate, FeedService.mutate
Tags: AdGroupAdService.mutate
"""

__author__ = ('api.msaniscalchi@gmail.com (Mark Saniscalchi)',
              'yufeng.dev@gmail.com (Yufeng Guo)')

# Import appropriate classes from the client library.
from googleads import adwords

# See the Placeholder reference page for a list of all the placeholder types
# and fields:
# https://developers.google.com/adwords/api/docs/appendix/placeholders
PLACEHOLDER_AD_CUSTOMIZER = '10'
PLACEHOLDER_FIELD_INTEGER = '1'
PLACEHOLDER_FIELD_FLOAT = '2'
PLACEHOLDER_FIELD_PRICE = '3'
PLACEHOLDER_FIELD_DATE = '4'
PLACEHOLDER_FIELD_STRING = '5'

ADGROUPS = [
    'INSERT_ADGROUP_ID_HERE',
    'INSERT_ADGROUP_ID_HERE'
]

FEEDNAME = 'INSERT_FEED_NAME_HERE'


def main(client, adgroups):
  # Initialize appropriate services.
  ad_group_ad_service = client.GetService('AdGroupAdService', version='v201409')
  customer_feed_service = client.GetService(
      'CustomerFeedService', version='v201409')
  feed_item_service = client.GetService('FeedItemService', version='v201409')
  feed_mapping_service = client.GetService(
      'FeedMappingService', version='v201409')
  feed_service = client.GetService('FeedService', version='v201409')

  # First, create a customizer feed. One feed per account can be used for all
  # ads.
  customizer_feed = {
      'name': FEEDNAME,
      'attributes': [
          {'type': 'STRING', 'name': 'Name'},
          {'type': 'STRING', 'name': 'Price'},
          {'type': 'DATE_TIME', 'name': 'Date'}
      ]
  }

  feed_service_operation = {
      'operator': 'ADD',
      'operand': customizer_feed
  }

  response = feed_service.mutate([feed_service_operation])

  if response and 'value' in response:
    feed = response['value'][0]
    feed_data = {
        'feedId': feed['id'],
        'nameId': feed['attributes'][0]['id'],
        'priceId': feed['attributes'][1]['id'],
        'dateId': feed['attributes'][2]['id']
    }
    print ('Feed with name \'%s\' and ID %s was added with:'
           '\tName attribute ID %s and price attribute ID %s and date attribute'
           'ID %s') % (feed['name'], feed['id'], feed_data['nameId'],
                       feed_data['priceId'], feed_data['dateId'])
  else:
    raise Exception('No feeds were added')

  # Creating feed mapping to map the fields with customizer IDs.
  feed_mapping = {
      'placeholderType': PLACEHOLDER_AD_CUSTOMIZER,
      'feedId': feed_data['feedId'],
      'attributeFieldMappings': [
          {
              'feedAttributeId': feed_data['nameId'],
              'fieldId': PLACEHOLDER_FIELD_STRING
          },
          {
              'feedAttributeId': feed_data['priceId'],
              'fieldId': PLACEHOLDER_FIELD_PRICE
          },
          {
              'feedAttributeId': feed_data['dateId'],
              'fieldId': PLACEHOLDER_FIELD_DATE
          }
      ]
  }

  feed_mapping_operation = {
      'operator': 'ADD',
      'operand': feed_mapping
  }

  response = feed_mapping_service.mutate([feed_mapping_operation])

  if response and 'value' in response:
    feed_mapping = response['value'][0]
    print ('Feed mapping with ID %s and placeholder type %s was saved for feed'
           ' with ID %s.') % (feed_mapping['feedMappingId'],
                              feed_mapping['placeholderType'],
                              feed_mapping['feedId'])
  else:
    raise Exception('No feed mappings were added.')

  # Now adding feed items -- the values we'd like to place.
  items_data = [
      {
          'name': 'Mars',
          'price': '$1234.56',
          'date': '20140601 000000',
          'adGroupId': adgroups[0]
      },
      {
          'name': 'Venus',
          'price': '$1450.00',
          'date': '20140615 120000',
          'adGroupId': adgroups[1]
      }
  ]

  feed_items = [{'feedId': feed_data['feedId'],
                 'adGroupTargeting': {
                     'TargetingAdGroupId': item['adGroupId']
                 },
                 'attributeValues': [
                     {
                         'feedAttributeId': feed_data['nameId'],
                         'stringValue': item['name']
                     },
                     {
                         'feedAttributeId': feed_data['priceId'],
                         'stringValue': item['price']
                     },
                     {
                         'feedAttributeId': feed_data['dateId'],
                         'stringValue': item['date']
                     }
                 ]} for item in items_data]

  feed_item_operations = [{
      'operator': 'ADD',
      'operand': feed_item
  } for feed_item in feed_items]

  response = feed_item_service.mutate(feed_item_operations)

  if response and 'value' in response:
    for feed_item in response['value']:
      print 'Feed item with ID %s was added.' % feed_item['feedItemId']
  else:
    raise Exception('No feed items were added.')

  # Finally, creating a customer (account-level) feed with a matching function
  # that determines when to use this feed. For this case we use the "IDENTITY"
  # matching function that is always 'true' just to associate this feed with
  # the customer. The targeting is done within the feed items using the
  # :campaign_targeting, :ad_group_targeting, or :keyword_targeting attributes.
  matching_function = {
      'operator': 'IDENTITY',
      'lhsOperand': [
          {
              'xsi_type': 'ConstantOperand',
              'type': 'BOOLEAN',
              'booleanValue': 'true'
          }
      ]
  }

  customer_feed = {
      'feedId': feed_data['feedId'],
      'matchingFunction': matching_function,
      'placeholderTypes': [PLACEHOLDER_AD_CUSTOMIZER]
  }

  customer_feed_operation = {
      'operator': 'ADD',
      'operand': customer_feed
  }

  response = customer_feed_service.mutate([customer_feed_operation])

  if response and 'value' in response:
    feed = response['value'][0]
    print 'Customer feed with ID %s was added.' % feed['feedId']
  else:
    raise Exception('No customer feeds were added.')

  # All set! We can now create ads with customizations.
  text_ad = {
      'xsi_type': 'TextAd',
      'headline': 'Luxury Cruise to {=%s.Name}' % FEEDNAME,
      'description1': 'Only {=%s.Price}' % FEEDNAME,
      'description2': 'Offer ends in {=countdown(%s.Date)}!' % FEEDNAME,
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
  } for adgroup in adgroups]

  print operations

  response = ad_group_ad_service.mutate(operations)

  print '===ad group ad service==='
  print response

  if response and 'value' in response:
    for ad in response['value']:
      print ('\tCreated an ad with ID \'%s\', type \'%s\', and status \'%s\'.'
             % (ad['ad']['id'], ad['ad']['Ad.Type'], ad['status']))
  else:
    raise Exception('No ads were added.')


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()
  main(adwords_client, ADGROUPS)
