#!/usr/bin/python
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

"""Creates a trial and waits for it to complete.

See the Campaign Drafts and Experiments guide for more information:
https://developers.google.com/adwords/api/docs/guides/campaign-drafts-experiments

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


import time
import uuid
from googleads import adwords


BASE_CAMPAIGN_ID = 'INSERT_BASE_CAMPAIGN_ID_HERE'
DRAFT_ID = 'INSERT_DRAFT_ID_HERE'
MAX_POLL_ATTEMPTS = 6


def main(client, base_campaign_id, draft_id):
  # Initialize appropriate services.
  trial_service = client.GetService('TrialService', version='v201702')
  trial_async_error_service = client.GetService('TrialAsyncErrorService',
                                                version='v201702')

  trial = {
      'draftId': draft_id,
      'baseCampaignId': base_campaign_id,
      'name': 'Test Trial #%d' % uuid.uuid4(),
      'trafficSplitPercent': 50
  }

  trial_operation = {'operator': 'ADD', 'operand': trial}
  trial_id = trial_service.mutate([trial_operation])['value'][0]['id']
  selector = {
      'fields': ['Id', 'Status', 'BaseCampaignId', 'TrialCampaignId'],
      'predicates': [{
          'field': 'Id',
          'operator': 'IN',
          'values': [trial_id]
      }]
  }

  # Since creating a trial is asynchronous, we have to poll it to wait for it to
  # finish.
  poll_attempts = 0
  is_pending = True
  trial = None

  while is_pending and poll_attempts < MAX_POLL_ATTEMPTS:
    trial = trial_service.get(selector)['entries'][0]
    print 'Trial ID %d has status "%s"' % (trial['id'], trial['status'])
    poll_attempts += 1
    is_pending = trial['status'] == 'CREATING'

    if is_pending:
      sleep_seconds = 30 * (2 ** poll_attempts)
      print 'Sleeping for %d seconds.' % sleep_seconds
      time.sleep(sleep_seconds)

  if trial['status'] == 'ACTIVE':
    # The trial creation was successful.
    print 'Trial created with ID %d and trial campaign ID %d' % (
        trial['id'], trial['trialCampaignId'])
  elif trial['status'] == 'CREATION_FAILED':
    # The trial creation failed, and errors can be fetched from the
    # TrialAsyncErrorService.
    selector = {
        'fields': ['TrialId', 'AsyncError'],
        'predicates': [{
            'field': 'TrialId',
            'operator': 'IN',
            'values': [trial['id']]
        }]
    }

    errors = trial_async_error_service.get(selector)['entries']

    if not errors:
      print 'Could not retrieve errors for trial %d' % trial['id']
    else:
      print 'Could not create trial due to the following errors:'
      for error in errors:
        print 'Error: %s' % error['asyncError']
  else:
    # Most likely, the trial is still being created. You can continue polling,
    # but we have limited the number of attempts in the example.
    print ('Timed out waiting to create trial from draft %d with base campaign '
           '%d' % (draft_id, base_campaign_id))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, BASE_CAMPAIGN_ID, DRAFT_ID)
