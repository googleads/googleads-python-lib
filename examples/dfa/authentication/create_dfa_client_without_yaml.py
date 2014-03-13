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

"""Initializes a DfaClient without using yaml-cached credentials.

While our LoadFromStorage method provides a useful shortcut to instantiate a
client if you regularly use just one set of credentials, production applications
may need to swap out users. This example shows you how to create an OAuth 2.0
client and a DfaClient without relying on a yaml file.
"""

__author__ = 'Joseph DiLallo'

from googleads import dfa
from googleads import oauth2

# OAuth 2.0 credential information. In a real application, you'd probably be
# pulling these values from a credential storage.
CLIENT_ID = 'INSERT_CLIENT_ID_HERE'
CLIENT_SECRET = 'INSERT_CLIENT_SECRET_HERE'
REFRESH_TOKEN = 'INSERT_REFRESH_TOKEN_HERE'

# DFA API information.
USER_PROFILE_NAME = 'INSERT_USER_PROFILE_NAME_HERE'
APPLICATION_NAME = 'INSERT_APPLICATION_NAME_HERE'


def main(client_id, client_secret, refresh_token, user_profile_name,
         application_name):
  oauth2_client = oauth2.GoogleRefreshTokenClient(
      client_id, client_secret, refresh_token)

  dfa_client = dfa.DfaClient(user_profile_name, oauth2_client, application_name)

  results = dfa_client.GetService('CampaignService').getCampaignsByCriteria({})
  if results['records']:
    for campaign in results['records']:
      print ('Campaign with name \'%s\' and ID \'%s\' was found.'
             % (campaign['name'], campaign['id']))


if __name__ == '__main__':
  main(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, USER_PROFILE_NAME,
       APPLICATION_NAME)
