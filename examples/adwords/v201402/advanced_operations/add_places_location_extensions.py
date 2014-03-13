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


"""Adds a feed that syncs feed items from a Google Places account.

This example associates the feed with a customer.

Tags: CustomerFeedService.mutate, FeedService.mutate
"""

__author__ = ('api.msaniscalchi@gmail.com (Mark Saniscalchi)',
              'Joseph DiLallo')

import time
import uuid

# Import appropriate classes from the client library.
import suds

from googleads import adwords
from googleads import errors

PLACES_EMAIL_ADDRESS = 'INSERT_PLACES_EMAIL_ADDRESS_HERE'
# To obtain an access token for your Places account, you can run the
# generate_refresh_token.py example and manually replace the scope with
# "https://www.google.com/local/add".
PLACES_ACCESS_TOKEN = 'INSERT_PLACES_OAUTH_ACCESS_TOKEN_HERE'

# The placeholder type for location extensions.
# See the Placeholder reference page for a list of all the placeholder types
# and fields:
# https://developers.google.com/adwords/api/docs/appendix/placeholders
PLACEHOLDER_LOCATION = 7

# The maximum number of CustomerFeed ADD operation attempts to make before
# throwing an exception.
MAX_CUSTOMER_FEED_ADD_ATTEMPTS = 10


def main(client, places_email_address, places_access_token):
  # Create a feed that will sync to the Google Places account specified by
  # places_email_address. Do not add FeedAttributes to this object,
  # as AdWords will add them automatically because this will be a
  # system generated feed.
  feed = {
      'name': 'Places feed #%s' % uuid.uuid4(),
      'systemFeedGenerationData': {
          'xsi_type': 'PlacesLocationFeedData',
          'oAuthInfo': {
              'httpMethod': 'GET',
              'httpRequestUrl': 'https://www.google.com/local/add',
              'httpAuthorizationHeader': 'Bearer %s' % places_access_token
          },
          'emailAddress': places_email_address,
      },
      # Since this feed's feed items will be managed by AdWords, you must set
      # its origin to ADWORDS.
      'origin': 'ADWORDS'
  }

  # Create an operation to add the feed.
  places_operations = [{
      'operator': 'ADD',
      'operand': feed
  }]

  places_response = client.GetService('FeedService', version='v201402').mutate(
      places_operations)
  added_feed = places_response['value'][0]
  print 'Added places feed with ID: %d\n' % added_feed['id']

  # Add a CustomerFeed that associates the feed with this customer for the
  # LOCATION placeholder type.
  customer_feed = {
      'feedId': added_feed['id'],
      'placeholderTypes': [PLACEHOLDER_LOCATION],
      'matchingFunction': {
          'operator': 'IDENTITY',
          'lhsOperand': {
              'xsi_type': 'FunctionArgumentOperand',
              'type': 'BOOLEAN',
              'booleanValue': True
          }
      }
  }

  customer_feed_operation = {
      'xsi_type': 'CustomerFeedOperation',
      'operator': 'ADD',
      'operand': customer_feed
  }

  customer_feed_service = client.GetService(
      'CustomerFeedService', version='v201402')
  added_customer_feed = None

  i = 0
  while i < MAX_CUSTOMER_FEED_ADD_ATTEMPTS and added_customer_feed is None:
    try:
      added_customer_feed = customer_feed_service.mutate([
          customer_feed_operation])['value'][0]
    except suds.WebFault:
      # Wait using exponential backoff policy
      sleep_seconds = 2**i
      print ('Attempt %d to add the CustomerFeed was not successful.'
             'Waiting %d seconds before trying again.\n' % (i, sleep_seconds))
      time.sleep(sleep_seconds)
    i += 1

  if added_customer_feed is None:
    raise errors.GoogleAdsError(
        'Could not create the CustomerFeed after %s attempts. Please retry the '
        'CustomerFeed ADD operation later.' % MAX_CUSTOMER_FEED_ADD_ATTEMPTS)

  print ('Added CustomerFeed for feed ID %d and placeholder type %d\n'
         % (added_customer_feed['id'], added_customer_feed['placeholderTypes']))

if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()
  main(adwords_client, PLACES_EMAIL_ADDRESS, PLACES_ACCESS_TOKEN)
