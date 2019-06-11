#!/usr/bin/env python
#
# Copyright 2016 Google Inc. All Rights Reserved.
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

"""This example gets all campaigns with AWQL.

To add a campaign, run add_campaign.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


from googleads import adwords


PAGE_SIZE = 100


def main(client):
  # Initialize appropriate service.
  campaign_service = client.GetService('CampaignService', version='v201809')

  # Construct query and get all campaigns.
  query = (adwords.ServiceQueryBuilder()
           .Select('Id', 'Name', 'Status')
           .Where('Status').EqualTo('ENABLED')
           .OrderBy('Name')
           .Limit(0, PAGE_SIZE)
           .Build())

  for page in query.Pager(campaign_service):
    # Display results.
    if 'entries' in page:
      for campaign in page['entries']:
        print('Campaign with id "%s", name "%s", and status "%s" was '
              'found.' % (campaign['id'], campaign['name'],
                          campaign['status']))
    else:
      print('No campaigns were found.')


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()
  main(adwords_client)
