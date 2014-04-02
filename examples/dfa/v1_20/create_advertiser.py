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

"""This example creates an advertiser in a given DFA network.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: advertiser.saveAdvertiser
"""

__author__ = 'Joseph DiLallo'

import uuid

# Import appropriate modules from the client library.
from googleads import dfa


def main(client):
  # Initialize appropriate service.
  advertiser_service = client.GetService(
      'advertiser', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Construct and save advertiser.
  advertiser = {
      'name': 'Advertiser %s' % uuid.uuid4(),
      'approved': 'true'
  }

  result = advertiser_service.saveAdvertiser(advertiser)

  # Display results.
  print 'Advertiser with ID \'%s\' was created.' % result['id']


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client)
