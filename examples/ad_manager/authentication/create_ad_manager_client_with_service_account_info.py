#!/usr/bin/env python
#
# Copyright 2024 Google Inc. All Rights Reserved.
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

"""Initializes a AdManagerClient using a Service Account info dictionary."""

import json

from googleads import ad_manager
from googleads import oauth2

# OAuth2 credential information. In a real application, you'd probably be
# pulling these values from a credential storage or environment variable.
# For this example, we'll load them from a JSON file.
KEY_FILE = 'INSERT_KEY_FILE_PATH'

# Ad Manager API information.
APPLICATION_NAME = 'INSERT_APPLICATION_NAME_HERE'


def main(key_file, application_name):
  # Load the service account info from a JSON file
  with open(key_file, 'r') as json_file:
    service_account_info = json.load(json_file)
  
  # In a real application, you might get this info from:
  # - Environment variables
  # - A secret manager
  # - A database
  # - Any other secure storage

  # Create the OAuth2 client using the service account info dictionary
  oauth2_client = oauth2.GoogleServiceAccountClient.from_service_account_info(
      service_account_info, oauth2.GetAPIScope('ad_manager'))

  # Create the Ad Manager client
  ad_manager_client = ad_manager.AdManagerClient(
      oauth2_client, application_name)

  # Make an API call to verify everything is working
  networks = ad_manager_client.GetService('NetworkService').getAllNetworks()
  for network in networks:
    print('Network with network code "%s" and display name "%s" was found.'
          % (network['networkCode'], network['displayName']))


if __name__ == '__main__':
  main(KEY_FILE, APPLICATION_NAME) 