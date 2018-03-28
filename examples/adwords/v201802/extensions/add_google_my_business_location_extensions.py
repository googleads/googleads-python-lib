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


"""Adds a feed that syncs feed items from a Google My Business (GMB) account.

This example associates the feed with a customer.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


import time
import uuid

from googleads import adwords
from googleads import errors

GMB_EMAIL_ADDRESS = 'INSERT_GMB_EMAIL_ADDRESS_HERE'

# If the gmb_email_address above is for a GMB manager instead of
# the GMB account owner, then set business_account_identifier to the
# +Page ID of a location for which the manager has access. See the
# location extensions guide at
# https://developers.google.com/adwords/api/docs/guides/feed-services-locations
# for details.
BUSINESS_ACCOUNT_IDENTIFIER = None

# The placeholder type for location extensions.
# See the Placeholder reference page for a list of all the placeholder types
# and fields:
# https://developers.google.com/adwords/api/docs/appendix/placeholders
PLACEHOLDER_LOCATION = 7

# The maximum number of CustomerFeed ADD operation attempts to make before
# throwing an exception.
MAX_CUSTOMER_FEED_ADD_ATTEMPTS = 10


def main(client, gmb_email_address, gmb_access_token,
         business_account_identifier=None):
  # Create a feed that will sync to the Google Places account specified by
  # gmb_email_address. Do not add FeedAttributes to this object,
  # as AdWords will add them automatically because this will be a
  # system generated feed.
  feed = {
      'name': 'GMB feed #%s' % uuid.uuid4(),
      'systemFeedGenerationData': {
          'xsi_type': 'PlacesLocationFeedData',
          'oAuthInfo': {
              'httpMethod': 'GET',
              'httpRequestUrl': 'https://www.googleapis.com/auth/adwords',
              'httpAuthorizationHeader': 'Bearer %s' % gmb_access_token
          },
          'emailAddress': gmb_email_address,
      },
      # Since this feed's feed items will be managed by AdWords, you must set
      # its origin to ADWORDS.
      'origin': 'ADWORDS'
  }

  # Only include the business_account_identifier if it's specified.
  if business_account_identifier:
    feed['systemFeedGenerationData']['businessAccountIdentifier'] = (
        business_account_identifier
    )

  # Create an operation to add the feed.
  gmb_operations = [{
      'operator': 'ADD',
      'operand': feed
  }]

  gmb_response = client.GetService('FeedService', version='v201802').mutate(
      gmb_operations)
  added_feed = gmb_response['value'][0]
  print 'Added GMB feed with ID: %d\n' % added_feed['id']

  # Add a CustomerFeed that associates the feed with this customer for the
  # LOCATION placeholder type.
  customer_feed = {
      'feedId': added_feed['id'],
      'placeholderTypes': [PLACEHOLDER_LOCATION],
      # Create a matching function that will always evaluate to True.
      'matchingFunction': {
          'operator': 'IDENTITY',
          'lhsOperand': {
              'xsi_type': 'ConstantOperand',
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
      'CustomerFeedService', version='v201802')
  added_customer_feed = None

  i = 0
  while i < MAX_CUSTOMER_FEED_ADD_ATTEMPTS and added_customer_feed is None:
    try:
      added_customer_feed = customer_feed_service.mutate([
          customer_feed_operation])['value'][0]
    except errors.GoogleAdsServerFault:
      # Wait using exponential backoff policy
      sleep_seconds = 2 ** i
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

  # If the GMB_EMAIL_ADDRESS above is the same user you used to generate your
  # AdWords API refresh token, leave the assignment below unchanged. Otherwise,
  # to obtain an access token for your GMB account, you can run the
  # generate_refresh_token.py example after manually replacing the scope with
  # "https://www.google.com/local/add".
  GMB_ACCESS_TOKEN = adwords_client.oauth2_client.oauth2credentials.access_token

  main(adwords_client, GMB_EMAIL_ADDRESS, GMB_ACCESS_TOKEN,
       BUSINESS_ACCOUNT_IDENTIFIER)
