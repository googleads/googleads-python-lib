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

"""Demonstrates how to find and remove shared sets/shared set criterions.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: CampaignSharedSetService.get, SharedCriterionService.get,
      SharedCriterionService.mutate
"""

__author__ = 'Mark Saniscalchi'

from googleads import adwords


CAMPAIGN_ID = 'INSERT_CAMPAIGN_ID_HERE'
PAGE_SIZE = 500


def main(client, campaign_id):
  # Initialize appropriate services.
  shared_criterion_service = client.GetService('SharedCriterionService',
                                               version='v201506')
  campaign_shared_set_service = client.GetService('CampaignSharedSetService',
                                                  version='v201506')

  shared_set_ids = []
  criterion_ids = []

  # First, retrieve all shared sets associated with the campaign.

  # Create selector for shared sets to:
  # - filter by campaign ID,
  # - filter by shared set type.
  selector = {
      'fields': ['SharedSetId', 'CampaignId', 'SharedSetName', 'SharedSetType',
                 'Status'],
      'predicates': [
          {
              'field': 'CampaignId',
              'operator': 'EQUALS',
              'values': [campaign_id]
          },
          {
              'field': 'SharedSetType',
              'operator': 'IN',
              'values': ['NEGATIVE_KEYWORDS', 'NEGATIVE_PLACEMENTS']
          }
      ],
      'paging': {
          'startIndex': 0,
          'numberResults': PAGE_SIZE
      }
  }

  # Set initial values:
  offset = 0
  page = {'totalNumEntries': 1}

  while page['totalNumEntries'] > offset:
    page = campaign_shared_set_service.get(selector)
    if 'entries' in page:
      for shared_set in page['entries']:
        print 'Campaign shared set ID %d and name "%s"' % (
            shared_set['sharedSetId'], shared_set['sharedSetName']
        )
        shared_set_ids.append(shared_set['sharedSetId'])
    # Increment values to request the next page.
    offset += PAGE_SIZE
    selector['paging']['startIndex'] = offset

  # Next, retrieve criterion IDs for all found shared sets.
  selector = {
      'fields': ['SharedSetId', 'Id', 'KeywordText', 'KeywordMatchType',
                 'PlacementUrl'],
      'predicates': [
          {
              'field': 'SharedSetId',
              'operator': 'IN',
              'values': shared_set_ids
          }
      ],
      'paging': {
          'startIndex': 0,
          'numberResults': PAGE_SIZE
      }
  }

  # Set initial values:
  offset = 0
  page = {'totalNumEntries': 1}

  while page['totalNumEntries'] > offset:
    page = shared_criterion_service.get(selector)
    if page['entries']:
      for shared_criterion in page['entries']:
        if shared_criterion['criterion']['type'] == 'KEYWORD':
          print ('Shared negative keyword with ID %d and text "%s" was'
                 'found.' % (shared_criterion['criterion']['id'],
                             shared_criterion['criterion']['text']))
        elif shared_criterion['criterion']['type'] == 'PLACEMENT':
          print ('Shared negative placement with ID %d and url "%s" was'
                 'found.' % (shared_criterion['criterion']['id'],
                             shared_criterion['criterion']['url']))
        else:
          print 'Shared criterion with ID %d was found.' % (
              shared_criterion['criterion']['id'],
          )
        criterion_ids.append({
            'sharedSetId': shared_criterion['sharedSetId'],
            'criterionId': shared_criterion['criterion']['id']
        })
    # Increment values to request the next page.
    offset += PAGE_SIZE
    selector['paging']['startIndex'] = offset

  # Finally, remove the criteria.
  operations = [
      {
          'operator': 'REMOVE',
          'operand': {
              'criterion': {'id': criterion['criterionId']},
              'sharedSetId': criterion['sharedSetId']
          }
      } for criterion in criterion_ids
  ]

  response = shared_criterion_service.mutate(operations)
  if 'value' in response:
    for criterion in response['value']:
      print ('Criterion ID %d was successfully removed from shared set ID'
             '%d.' % (criterion['criterion']['id'], criterion['sharedSetId']))
  else:
    print 'No shared criteria were removed.'


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, CAMPAIGN_ID)
