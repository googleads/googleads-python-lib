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

"""Initializes an AdWordsClient without using yaml-cached credentials.

While our LoadFromStorage method provides a useful shortcut to instantiate a
client if you regularly use just one set of credentials, production applications
may need to swap out users. This example shows you how to create an OAuth2
client and an AdWordsClient without relying on a yaml file.
"""


from googleads import adwords
from googleads import oauth2

# OAuth2 credential information. In a real application, you'd probably be
# pulling these values from a credential storage.
CLIENT_ID = 'INSERT_CLIENT_ID_HERE'
CLIENT_SECRET = 'INSERT_CLIENT_SECRET_HERE'
REFRESH_TOKEN = 'INSERT_REFRESH_TOKEN_HERE'

# AdWords API information.
DEVELOPER_TOKEN = 'INSERT_DEVELOPER_TOKEN_HERE'
USER_AGENT = 'INSERT_USER_AGENT_HERE'
CLIENT_CUSTOMER_ID = 'INSERT_CLIENT_CUSTOMER_ID_HERE'


def main(client_id, client_secret, refresh_token, developer_token, user_agent,
         client_customer_id):
  oauth2_client = oauth2.GoogleRefreshTokenClient(
      client_id, client_secret, refresh_token)

  adwords_client = adwords.AdWordsClient(
      developer_token, oauth2_client, user_agent,
      client_customer_id=client_customer_id)

  customer_service = adwords_client.GetService('CustomerService',
                                               version='v201702')
  customers = customer_service.getCustomers()

  print 'You are logged in as a user with access to the following customers:'

  for customer in customers:
    print '\t%s' % customer['customerId']


if __name__ == '__main__':
  main(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, DEVELOPER_TOKEN, USER_AGENT,
       CLIENT_CUSTOMER_ID)
