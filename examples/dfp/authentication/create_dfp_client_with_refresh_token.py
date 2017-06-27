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

"""Initializes a DfpClient without using yaml-cached credentials.

While our LoadFromStorage method provides a useful shortcut to instantiate a
client if you regularly use just one set of credentials, production applications
may need to swap out users. This example shows you how to create an OAuth2
client and a DfpClient without relying on a yaml file.
"""


from googleads import dfp
from googleads import oauth2

# OAuth2 credential information. In a real application, you'd probably be
# pulling these values from a credential storage.
CLIENT_ID = 'INSERT_CLIENT_ID_HERE'
CLIENT_SECRET = 'INSERT_CLIENT_SECRET_HERE'
REFRESH_TOKEN = 'INSERT_REFRESH_TOKEN_HERE'

# DFP API information.
APPLICATION_NAME = 'INSERT_APPLICATION_NAME_HERE'


def main(client_id, client_secret, refresh_token, application_name):
  oauth2_client = oauth2.GoogleRefreshTokenClient(
      client_id, client_secret, refresh_token)

  dfp_client = dfp.DfpClient(oauth2_client, application_name)

  networks = dfp_client.GetService('NetworkService').getAllNetworks()
  for network in networks:
    print ('Network with network code "%s" and display name "%s" was found.'
           % (network['networkCode'], network['displayName']))


if __name__ == '__main__':
  main(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, APPLICATION_NAME)
