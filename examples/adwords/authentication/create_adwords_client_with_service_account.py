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

"""Initializes an AdWordsClient via impersonation using a Service Account."""


from googleads import adwords
from googleads import oauth2

# OAuth2 credential information. In a real application, you'd probably be
# pulling these values from a credential storage.
SERVICE_ACCOUNT_EMAIL = 'INSERT_SERVICE_ACCOUNT_EMAIL_HERE'
KEY_FILE = 'INSERT_PATH_TO_KEY_FILE'
SERVICE_ACCOUNT_USER = 'INSERT_IMPERSONATED_EMAIL_HERE'

# AdWords API information.
DEVELOPER_TOKEN = 'INSERT_DEVELOPER_TOKEN_HERE'
USER_AGENT = 'INSERT_USER_AGENT_HERE'
CLIENT_CUSTOMER_ID = 'INSERT_CLIENT_CUSTOMER_ID_HERE'


def main(service_account_email, key_file, service_account_user,
         developer_token, user_agent, client_customer_id):
  oauth2_client = oauth2.GoogleServiceAccountClient(
      oauth2.GetAPIScope('adwords'), service_account_email, key_file,
      sub=service_account_user)

  adwords_client = adwords.AdWordsClient(
      developer_token, oauth2_client, user_agent, client_customer_id)

  customer = adwords_client.GetService('CustomerService').get()
  print 'You are logged in as customer: %s' % customer['customerId']


if __name__ == '__main__':
  main(SERVICE_ACCOUNT_EMAIL, KEY_FILE, SERVICE_ACCOUNT_USER,
       DEVELOPER_TOKEN, USER_AGENT, CLIENT_CUSTOMER_ID)
