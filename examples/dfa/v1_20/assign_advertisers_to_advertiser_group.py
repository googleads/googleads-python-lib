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

"""This example assigns a list of advertisers to an advertiser group.

CAUTION: An advertiser that has campaigns associated with it cannot be
removed from an advertiser group once assigned.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import dfa


ADVERTISER_IDS = ['INSERT_FIRST_ADVERTISER_ID_HERE',
                  'INSERT_SECOND_ADVERTISER_ID_HERE']
ADVERTISER_GROUP_IDS = 'INSERT_ADVERTISER_GROUP_ID_HERE'


def main(client, advertiser_ids, advertiser_group_id):
  # Initialize appropriate service.
  advertiser_group_service = client.GetService(
      'advertisergroup', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Assign the advertisers to the advertiser group.
  advertiser_group_service.assignAdvertisersToAdvertiserGroup(
      advertiser_group_id, advertiser_ids)
  print 'Advertisers have been updated.'


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client, ADVERTISER_IDS, ADVERTISER_GROUP_IDS)
