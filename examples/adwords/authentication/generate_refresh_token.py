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

from oauth2client import client

# raw_input was renamed to input in python3
try:
    raw_input
except NameError:
    raw_input = input

# Your OAuth2 Client ID and Secret. If you do not have an ID and Secret yet,
# please go to https://console.developers.google.com and create a set.
DEFAULT_CLIENT_ID = None
DEFAULT_CLIENT_SECRET = None

# The AdWords API OAuth2 scope.
SCOPE = u'https://www.googleapis.com/auth/adwords'

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


def main(client_id, client_secret, scopes):
  """Retrieve and display the access and refresh token."""
  flow = client.OAuth2WebServerFlow(
      client_id=client_id,
      client_secret=client_secret,
      scope=scopes,
      user_agent='Ads Python Client Library',
      redirect_uri='urn:ietf:wg:oauth:2.0:oob')

  authorize_url = flow.step1_get_authorize_url()

  print ('Log into the Google Account you use to access your AdWords account'
         'and go to the following URL: \n%s\n' % (authorize_url))
  print 'After approving the token enter the verification code (if specified).'
  code = raw_input('Code: ').strip()

  try:
    credential = flow.step2_exchange(code)
  except client.FlowExchangeError, e:
    print 'Authentication has failed: %s' % e
    sys.exit(1)
  else:
    print ('OAuth2 authorization successful!\n\n'
           'Your access token is:\n %s\n\nYour refresh token is:\n %s'
           % (credential.access_token, credential.refresh_token))


if __name__ == '__main__':
  args = parser.parse_args()
  configured_scopes = [SCOPE]
  if not (any([args.client_id, DEFAULT_CLIENT_ID]) and
          any([args.client_secret, DEFAULT_CLIENT_SECRET])):
    raise AttributeError('No client_id or client_secret specified.')
  if args.additional_scopes:
    configured_scopes.extend(args.additional_scopes.replace(' ', '').split(','))
  main(args.client_id, args.client_secret, configured_scopes)
