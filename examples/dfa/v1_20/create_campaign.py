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

"""This example creates a campaign in a given advertiser.

To create an advertiser, run create_advertiser.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import dfa


ADVERTISER_ID = 'INSERT_ADVERTISER_ID_HERE'
CAMPAIGN_NAME = 'INSERT_CAMPAIGN_NAME_HERE'
URL = 'INSERT_LANDING_PAGE_URL_HERE'
LANDING_PAGE_NAME = 'INSERT_LANDING_PAGE_NAME_HERE'
START_DATE = '%(year)s-%(month)02d-%(day)02dT12:00:00' % {
    'year': 'INSERT_START_YEAR_HERE',
    'month': int('INSERT_START_MONTH_HERE'),
    'day': int('INSERT_START_DAY_HERE')}
END_DATE = '%(year)s-%(month)02d-%(day)02dT12:00:00' % {
    'year': 'INSERT_END_YEAR_HERE',
    'month': int('INSERT_END_MONTH_HERE'),
    'day': int('INSERT_END_DAY_HERE')}


def main(client, advertiser_id, campaign_name, url, landing_page_name,
         start_date, end_date):
  # Initialize appropriate service.
  campaign_service = client.GetService(
      'campaign', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Create a default landing page for the campaign and save it.
  default_landing_page = {
      'url': url,
      'name': landing_page_name
  }

  default_landing_page_id = campaign_service.saveLandingPage(
      default_landing_page)['id']

  # Construct and save the campaign.
  campaign = {
      'name': campaign_name,
      'advertiserId': advertiser_id,
      'defaultLandingPageId': default_landing_page_id,
      'archived': 'false',
      'startDate': start_date,
      'endDate': end_date
  }
  result = campaign_service.saveCampaign(campaign)

  # Display results.
  print 'Campaign with ID \'%s\' was created.' % result['id']


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client, ADVERTISER_ID, CAMPAIGN_NAME, URL, LANDING_PAGE_NAME,
       START_DATE, END_DATE)
