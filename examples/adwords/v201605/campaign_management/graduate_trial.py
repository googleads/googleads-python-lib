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

"""Illustrates how to graduate a trial.

See the Campaign Drafts and Experiments guide for more information:
https://developers.google.com/adwords/api/docs/guides/campaign-drafts-experiments

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


import uuid
from googleads import adwords


TRIAL_ID = 'INSERT_TRIAL_ID_HERE'


def main(client, trial_id):
  # Initialize appropriate services.
  trial_service = client.GetService('TrialService', version='v201605')
  budget_service = client.GetService('BudgetService', version='v201605')

  # To graduate a trial, you must specify a different budget from the base
  # campaign. The base campaign (in order to have had a trial based on it) must
  # have a non-shared budget, so it cannot be shared with the new independent
  # campaign created by graduation.
  budget = {
      'name': 'Budget #%d' % uuid.uuid4(),
      'amount': {'microAmount': 50000000},
      'deliveryMethod': 'STANDARD'
  }

  budget_operation = {'operator': 'ADD', 'operand': budget}
  # Add budget
  budget_id = budget_service.mutate([budget_operation])['value'][0]['budgetId']

  trial = {
      'id': trial_id,
      'budgetId': budget_id,
      'status': 'GRADUATED'
  }

  trial_operation = {'operator': 'SET', 'operand': trial}

  # Update the trial.
  trial = trial_service.mutate([trial_operation])['value'][0]

  # Graduation is a synchronous operation, so the campaign is already ready. If
  # you promote instead, make sure to see the polling scheme demonstrated in
  # add_trial.py to wait for the asynchronous operation to finish.
  print ('Trial ID %d graduated. Campaign %d was given a new budget ID %d and '
         'is no longer dependent on this trial.' % (
             trial['id'], trial['trialCampaignId'], budget_id))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, TRIAL_ID)
