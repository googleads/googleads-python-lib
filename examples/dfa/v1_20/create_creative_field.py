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

"""This example creates a creative field associated with a given advertiser.

To get an advertiser ID, run get_advertisers.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: creativefield.saveCreativeField
"""

__author__ = 'Joseph DiLallo'

# Import appropriate modules from the client library.
from googleads import dfa


ADVERTISER_ID = 'INSERT_ADVERTISER_ID_HERE'
CREATIVE_FIELD_NAME = 'INSERT_CREATIVE_FIELD_NAME_HERE'


def main(client, advertiser_id, creative_field_name):
  # Initialize appropriate service.
  creative_field_service = client.GetService(
      'creativefield', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Construct and save creative field.
  creative_field = {
      'name': creative_field_name,
      'advertiserId': advertiser_id,
      'id': '-1'
  }
  result = creative_field_service.saveCreativeField(creative_field)

  # Display results.
  print 'Creative field with ID \'%s\' was created.' % result['id']


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client, ADVERTISER_ID, CREATIVE_FIELD_NAME)
