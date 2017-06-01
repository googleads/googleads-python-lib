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

"""Initializes a DfpClient using a Service Account."""


from googleads import dfp
from googleads import oauth2

# OAuth2 credential information. In a real application, you'd probably be
# pulling these values from a credential storage.
SERVICE_ACCOUNT_EMAIL = 'INSERT_SERVICE_ACCOUNT_EMAIL'
KEY_FILE = 'INSERT_KEY_FILE_PATH'

# DFP API information.
APPLICATION_NAME = 'INSERT_APPLICATION_NAME_HERE'


def main(service_account_email, key_file, application_name):
  oauth2_client = oauth2.GoogleServiceAccountClient(
      oauth2.GetAPIScope('dfp'), service_account_email, key_file)

  dfp_client = dfp.DfpClient(oauth2_client, application_name)

  networks = dfp_client.GetService('NetworkService').getAllNetworks()
  for network in networks:
    print ('Network with network code \'%s\' and display name \'%s\' was found.'
           % (network['networkCode'], network['displayName']))


if __name__ == '__main__':
  main(SERVICE_ACCOUNT_EMAIL, KEY_FILE, APPLICATION_NAME)
