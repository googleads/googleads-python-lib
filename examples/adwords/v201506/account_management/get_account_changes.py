#!/usr/bin/python
#
# Copyright 2015 Google Inc. All Rights Reserved.
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

"""This example gets the changes in the account during the last 24 hours.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


import datetime
from googleads import adwords


def main(client):
  # Initialize appropriate service.
  customer_sync_service = client.GetService(
      'CustomerSyncService', version='v201506')
  campaign_service = client.GetService('CampaignService', version='v201506')

  # Construct selector and get all campaigns.
  selector = {
      'fields': ['Id', 'Name', 'Status']
  }
  campaigns = campaign_service.get(selector)
  campaign_ids = []
  if 'entries' in campaigns:
    for campaign in campaigns['entries']:
      campaign_ids.append(campaign['id'])
  else:
    print 'No campaigns were found.'
    return

  # Construct selector and get all changes.
  today = datetime.datetime.today()
  yesterday = today - datetime.timedelta(1)
  selector = {
      'dateTimeRange': {
          'min': yesterday.strftime('%Y%m%d %H%M%S'),
          'max': today.strftime('%Y%m%d %H%M%S')
      },
      'campaignIds': campaign_ids
  }
  account_changes = customer_sync_service.get(selector)

  # Display results.
  if account_changes:
    if 'lastChangeTimestamp' in account_changes:
      print 'Most recent changes: %s' % account_changes['lastChangeTimestamp']
    if account_changes['changedCampaigns']:
      for data in account_changes['changedCampaigns']:
        print ('Campaign with id \'%s\' has change status \'%s\'.'
               % (data['campaignId'], data['campaignChangeStatus']))
        if (data['campaignChangeStatus'] != 'NEW' and
            data['campaignChangeStatus'] != 'FIELDS_UNCHANGED'):
          if 'addedAdExtensions' in data:
            print '  Added ad extensions: %s' % data['addedAdExtensions']
          if 'removedAdExtensions' in data:
            print '  Removed ad extensions: %s' % data['removedAdExtensions']
          if 'addedCampaignCriteria' in data:
            print ('  Added campaign criteria: %s' %
                   data['addedCampaignCriteria'])
          if 'removedCampaignCriteria' in data:
            print ('  Removed campaign criteria: %s' %
                   data['removedCampaignCriteria'])
          if 'changedAdGroups' in data:
            for ad_group_data in data['changedAdGroups']:
              print ('  Ad group with id \'%s\' has change status \'%s\'.'
                     % (ad_group_data['adGroupId'],
                        ad_group_data['adGroupChangeStatus']))
              if ad_group_data['adGroupChangeStatus'] != 'NEW':
                if 'changedAds' in ad_group_data:
                  print '    Changed ads: %s' % ad_group_data['changedAds']
                if 'changedCriteria' in ad_group_data:
                  print ('    Changed criteria: %s' %
                         ad_group_data['changedCriteria'])
                if 'removedCriteria' in ad_group_data:
                  print ('    Removed criteria: %s' %
                         ad_group_data['removedCriteria'])
  else:
    print 'No changes were found.'


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()
  main(adwords_client)
