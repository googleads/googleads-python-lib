#!/usr/bin/env python
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

"""Generates refresh token for AdWords using the Installed Application flow."""


import argparse
import sys

from google_auth_oauthlib.flow import InstalledAppFlow
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError

# Your OAuth2 Client ID and Secret. If you do not have an ID and Secret yet,
# please go to https://console.developers.google.com and create a set.
DEFAULT_CLIENT_ID = None
DEFAULT_CLIENT_SECRET = None

# The AdWords API OAuth2 scope.
SCOPE = u'https://www.googleapis.com/auth/adwords'
# The redirect URI set for the given Client ID. The redirect URI for Client ID
# generated for an installed application will always have this value.
_REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

parser = argparse.ArgumentParser(description='Generates a refresh token with '
                                 'the provided credentials.')
parser.add_argument('--client_id', default=DEFAULT_CLIENT_ID,
                    help='Client Id retrieved from the Developer\'s Console.')
parser.add_argument('--client_secret', default=DEFAULT_CLIENT_SECRET,
                    help='Client Secret retrieved from the Developer\'s '
                    'Console.')
parser.add_argument('--additional_scopes', default=None,
                    help='Additional scopes to apply when generating the '
                    'refresh token. Each scope should be separated by a comma.')


class ClientConfigBuilder(object):
  """Helper class used to build a client config dict used in the OAuth 2.0 flow.
  """
  _DEFAULT_AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
  _DEFAULT_TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
  CLIENT_TYPE_WEB = 'web'
  CLIENT_TYPE_INSTALLED_APP = 'installed'

  def __init__(self, client_type=None, client_id=None, client_secret=None,
               auth_uri=_DEFAULT_AUTH_URI, token_uri=_DEFAULT_TOKEN_URI):
    self.client_type = client_type
    self.client_id = client_id
    self.client_secret = client_secret
    self.auth_uri = auth_uri
    self.token_uri = token_uri

  def Build(self):
    """Builds a client config dictionary used in the OAuth 2.0 flow."""
    if all((self.client_type, self.client_id, self.client_secret,
            self.auth_uri, self.token_uri)):
      client_config = {
          self.client_type: {
              'client_id': self.client_id,
              'client_secret': self.client_secret,
              'auth_uri': self.auth_uri,
              'token_uri': self.token_uri
          }
      }
    else:
      raise ValueError('Required field is missing.')

    return client_config


def main(client_id, client_secret, scopes):
  """Retrieve and display the access and refresh token."""
  client_config = ClientConfigBuilder(
      client_type=ClientConfigBuilder.CLIENT_TYPE_WEB, client_id=client_id,
      client_secret=client_secret)

  flow = InstalledAppFlow.from_client_config(
      client_config.Build(), scopes=scopes)
  # Note that from_client_config will not produce a flow with the
  # redirect_uris (if any) set in the client_config. This must be set
  # separately.
  flow.redirect_uri = _REDIRECT_URI

  auth_url, _ = flow.authorization_url(prompt='consent')

  print('Log into the Google Account you use to access your AdWords account '
        'and go to the following URL: \n%s\n' % auth_url)
  print('After approving the token enter the verification code (if specified).')
  code = raw_input('Code: ').strip()

  try:
    flow.fetch_token(code=code)
  except InvalidGrantError as ex:
    print('Authentication has failed: %s' % ex)
    sys.exit(1)

  print('Access token: %s' % flow.credentials.token)
  print('Refresh token: %s' % flow.credentials.refresh_token)


if __name__ == '__main__':
  args = parser.parse_args()
  configured_scopes = [SCOPE]
  if not (any([args.client_id, DEFAULT_CLIENT_ID]) and
          any([args.client_secret, DEFAULT_CLIENT_SECRET])):
    raise AttributeError('No client_id or client_secret specified.')
  if args.additional_scopes:
    configured_scopes.extend(args.additional_scopes.replace(' ', '').split(','))
  main(args.client_id, args.client_secret, configured_scopes)
