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

"""This example gets all disapproved ads for a given campaign with AWQL.

To add an ad, run add_ads.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

from googleads import adwords


CAMPAIGN_ID = 'INSERT_CAMPAIGN_ID_HERE'


def main(client, campaign_id):
  # Initialize appropriate service.
  ad_group_ad_service = client.GetService('AdGroupAdService', version='v201702')

  # Construct query and get all ads for a given campaign.
  query = ('SELECT Id, AdGroupAdDisapprovalReasons '
           'WHERE CampaignId = %s AND '
           'AdGroupCreativeApprovalStatus = DISAPPROVED '
           'ORDER BY Id' % campaign_id)
  ads = ad_group_ad_service.query(query)

  # Display results.
  if 'entries' in ads:
    for ad in ads['entries']:
      print ('Ad with id \'%s\' was disapproved for the following reasons: '
             % (ad['ad']['id']))
      if ad['ad'].get('disapprovalReasons'):
        for reason in ad['ad']['disapprovalReasons']:
          print '\t%s' % reason
      else:
        print '\tReason not provided.'
  else:
    print 'No disapproved ads were found.'


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, CAMPAIGN_ID)
