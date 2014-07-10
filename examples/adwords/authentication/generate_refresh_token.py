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

"""Generates refresh token for AdWords using the Installed Application flow."""

__author__ = 'Joseph DiLallo'

import sys
import urllib2

from oauthlib import oauth2

# Your OAuth 2.0 Client ID and Secret. If you do not have an ID and Secret yet,
# please go to https://console.developers.google.com and create a set.
CLIENT_ID = 'INSERT_CLIENT_ID_HERE'
CLIENT_SECRET = 'INSERT_CLIENT_SECRET_HERE'

# You may optionally provide an HTTPS proxy.
HTTPS_PROXY = None

# The AdWords API OAuth 2.0 scope.
SCOPE = u'https://www.googleapis.com/auth/adwords'
# This callback URL will allow you to copy the token from the success screen.
CALLBACK_URL = 'urn:ietf:wg:oauth:2.0:oob'
# The HTTP headers needed on OAuth 2.0 refresh requests.
OAUTH2_REFRESH_HEADERS = {'content-type':
                          'application/x-www-form-urlencoded'}
# The web address for generating new OAuth 2.0 credentials at Google.
GOOGLE_OAUTH2_AUTH_ENDPOINT = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_OAUTH2_GEN_ENDPOINT = 'https://accounts.google.com/o/oauth2/token'


def main():
  oauthlib_client = oauth2.WebApplicationClient(CLIENT_ID)

  authorize_url = oauthlib_client.prepare_request_uri(
      GOOGLE_OAUTH2_AUTH_ENDPOINT, redirect_uri=CALLBACK_URL, scope=SCOPE)
  print ('Log in to your AdWords account and open the following URL: \n%s\n' %
         authorize_url)
  print 'After approving the token enter the verification code (if specified).'
  code = raw_input('Code: ').strip()

  post_body = oauthlib_client.prepare_request_body(
      client_secret=CLIENT_SECRET, code=code, redirect_uri=CALLBACK_URL)
  if sys.version_info[0] == 3:
    post_body = bytes(post_body, 'utf8')
  request = urllib2.Request(GOOGLE_OAUTH2_GEN_ENDPOINT, post_body,
                            OAUTH2_REFRESH_HEADERS)
  if HTTPS_PROXY:
    request.set_proxy(HTTPS_PROXY, 'https')
  raw_response = urllib2.urlopen(request).read().decode()
  oauth2_credentials = oauthlib_client.parse_request_body_response(raw_response)

  print ('Your access token is %s and your refresh token is %s'
         % (oauth2_credentials['access_token'],
            oauth2_credentials['refresh_token']))
  print ('You can cache these credentials into a yaml file with the '
         'following keys:\nadwords:\n  client_id: %s\n  client_secret: %s\n'
         '  refresh_token: %s\n'
         % (CLIENT_ID, CLIENT_SECRET, oauth2_credentials['refresh_token']))


if __name__ == '__main__':
  main()
