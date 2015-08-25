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

"""Initializes a DfaClient via impersonation using a Service Account."""


from googleads import dfa
from googleads import oauth2

# OAuth 2.0 credential information. In a real application, you'd probably be
# pulling these values from a credential storage.
SERVICE_ACCOUNT_EMAIL = 'INSERT_SERVICE_ACCOUNT_EMAIL_HERE'
KEY_FILE = 'INSERT_PATH_TO_KEY_FILE'
SERVICE_ACCOUNT_USER = 'INSERT_IMPERSONATED_EMAIL_HERE'

# DFA API information.
USER_PROFILE_NAME = 'INSERT_USER_PROFILE_NAME_HERE'
APPLICATION_NAME = 'INSERT_APPLICATION_NAME_HERE'


def main(service_account_email, key_file, service_account_user,
         user_profile_name, application_name):
  oauth2_client = oauth2.GoogleServiceAccountClient(
      oauth2.GetAPIScope('dfa'), service_account_email, key_file,
      sub=service_account_user)

  dfa_client = dfa.DfaClient(user_profile_name, oauth2_client, application_name)

  campaign_service = dfa_client.GetService(
      'campaign', server='https://advertisersapitest.doubleclick.net')
  results = campaign_service.getCampaignsByCriteria({})
  if results['records']:
    for campaign in results['records']:
      print ('Campaign with name \'%s\' and ID \'%s\' was found.'
             % (campaign['name'], campaign['id']))


if __name__ == '__main__':
  main(SERVICE_ACCOUNT_EMAIL, KEY_FILE, SERVICE_ACCOUNT_USER, USER_PROFILE_NAME,
       APPLICATION_NAME)
