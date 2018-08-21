#!/usr/bin/env python
#
# Copyright 2017 Google Inc. All Rights Reserved.
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

"""Initializes an AdManagerClient using GoogleAccessTokenClient.

Note that unlike clients initialized with GoogleRefreshTokenClient, those
initialized with GoogleAccessTokenClient can't refresh.
"""

import argparse
import datetime
from googleads import ad_manager
from googleads import oauth2
import httplib2
from oauth2client import client


GOOGLE_OAUTH2_ENDPOINT = 'https://accounts.google.com/o/oauth2/token'
USER_AGENT = 'INSERT_USER_AGENT_HERE'

# OAuth2 credential information.
DEFAULT_CLIENT_ID = 'INSERT_CLIENT_ID_HERE'
DEFAULT_CLIENT_SECRET = 'INSERT_CLIENT_SECRET_HERE'
DEFAULT_REFRESH_TOKEN = 'INSERT_REFRESH_TOKEN_HERE'

# Ad Manager API information.
DEFAULT_APPLICATION_NAME = 'INSERT_APPLICATION_NAME_HERE'

parser = argparse.ArgumentParser(
    description=('Creates an AdManagerClient using a GoogleAccessToken with an '
                 'access token generated with the given credentials.'))
parser.add_argument('--client_id', default=DEFAULT_CLIENT_ID,
                    help='Client Id retrieved from the Developer\'s Console.')
parser.add_argument('--client_secret', default=DEFAULT_CLIENT_SECRET,
                    help='Client Secret retrieved from the Developer\'s '
                    'Console.')
parser.add_argument('--refresh_token', default=DEFAULT_REFRESH_TOKEN,
                    help='The refresh token used to generate an access token.')
parser.add_argument('--application_name', default=DEFAULT_APPLICATION_NAME,
                    help='The application name for your Ad Manager account.')


def main(access_token, token_expiry, application_name):
  oauth2_client = oauth2.GoogleAccessTokenClient(access_token, token_expiry)

  ad_manager_client = ad_manager.AdManagerClient(
      oauth2_client, application_name)

  networks = ad_manager_client.GetService('NetworkService').getAllNetworks()
  for network in networks:
    print ('Network with network code "%s" and display name "%s" was found.'
           % (network['networkCode'], network['displayName']))


if __name__ == '__main__':
  args = parser.parse_args()

  # Retrieve a new access token for use in this example. In a production
  # application, you may use a credential store to share access tokens for a
  # given user across applications.
  oauth2credentials = client.OAuth2Credentials(
      None, args.client_id, args.client_secret, args.refresh_token,
      datetime.datetime(1980, 1, 1, 12), GOOGLE_OAUTH2_ENDPOINT,
      USER_AGENT)

  oauth2credentials.refresh(httplib2.Http())

  main(oauth2credentials.access_token, oauth2credentials.token_expiry,
       args.application_name)
