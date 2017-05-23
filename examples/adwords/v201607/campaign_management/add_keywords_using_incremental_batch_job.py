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

"""This uses the BatchJobService to incrementally create a complete Campaign.

The complete Campaign created by this example also includes AdGroups and
KeyWords.

"""

import random
import time
import urllib2
import uuid

from googleads import adwords


ADGROUP_ID = 'INSERT_ADGROUP_ID_HERE'
KEYWORD_COUNT = 100
MAX_POLL_ATTEMPTS = 5
PENDING_STATUSES = ('ACTIVE', 'AWAITING_FILE', 'CANCELING')


def main(client, adgroup_id):
  # Initialize BatchJobHelper.
  batch_job_helper = client.GetBatchJobHelper(version='v201607')
  # Create a BatchJob.
  batch_job = AddBatchJob(client)

  # Retrieve the URL used to upload the BatchJob operations.
  upload_url = batch_job['uploadUrl']['url']
  batch_job_id = batch_job['id']
  print 'Created BatchJob with ID "%d", status "%s", and upload URL "%s"' % (
      batch_job['id'], batch_job['status'], upload_url)

  # Initialize IncrementalUploadHelper.
  incremental_uploader = batch_job_helper.GetIncrementalUploadHelper(upload_url)

  # Generate and upload first set of operations.
  adgroup_criterion_operations = BuildAdGroupCriterionOperations(adgroup_id)
  incremental_uploader.UploadOperations(
      [adgroup_criterion_operations])
  # Generate and upload second set of operations.
  adgroup_criterion_operations = BuildAdGroupCriterionOperations(adgroup_id)
  incremental_uploader.UploadOperations(
      [adgroup_criterion_operations])
  # Generate and upload third and final set of operations.
  adgroup_criterion_operations = BuildAdGroupCriterionOperations(adgroup_id)
  incremental_uploader.UploadOperations(
      [adgroup_criterion_operations], is_last=True)

  # Download and display results.
  download_url = GetBatchJobDownloadUrlWhenReady(client, batch_job_id)
  response = urllib2.urlopen(download_url).read()
  PrintResponse(batch_job_helper, response)


def AddBatchJob(client):
  """Add a new BatchJob to upload operations to.

  Args:
    client: an instantiated AdWordsClient used to retrieve the BatchJob.

  Returns:
    The new BatchJob created by the request.
  """
  # Initialize appropriate service.
  batch_job_service = client.GetService('BatchJobService', version='v201607')
  # Create a BatchJob.
  batch_job_operations = [{
      'operand': {},
      'operator': 'ADD'
  }]
  return batch_job_service.mutate(batch_job_operations)['value'][0]


def BuildAdGroupCriterionOperations(adgroup_id):
  """Builds the operations adding a Keyword Criterion to each AdGroup.

  Args:
    adgroup_id: an integer identifying an AdGroup to associate the keywords
      with.

  Returns:
    a list containing the operations that will create a new Keyword Criterion
    associated with each provided AdGroup.
  """
  criterion_operations = [
      {
          # You must specify the xsi_type of operations run by the
          # BatchJobService.
          'xsi_type': 'AdGroupCriterionOperation',
          'operand': {
              'xsi_type': 'BiddableAdGroupCriterion',
              'adGroupId': adgroup_id,
              'criterion': {
                  'xsi_type': 'Keyword',
                  # Make 10% of keywords invalid to demonstrate error handling.
                  'text': 'mars%s%s' % (uuid.uuid4(),
                                        '!!!' if i % 10 == 0 else ''),
                  'matchType': 'BROAD'
              }
          },
          'operator': 'ADD'
      }
      for i in range(KEYWORD_COUNT)]

  return criterion_operations


def CancelBatchJob(client, batch_job, max_poll_attempts=MAX_POLL_ATTEMPTS):
  """Cancels the given BatchJob.

  Args:
    client: an instantiated AdWordsClient used to cancel the BatchJob.
    batch_job: a BatchJob to be canceled.
    max_poll_attempts: an int defining the number of times the the BatchJob will
      be checked to determine whether it has been canceled.
  """
  batch_job_service = client.GetService('BatchJobService', 'v201607')
  batch_job['status'] = 'CANCELING'

  operation = {
      'operator': 'SET',
      'operand': batch_job
  }

  batch_job_service.mutate([operation])

  # Verify that the Batch Job cancels.
  poll_attempt = 0

  while (poll_attempt in range(max_poll_attempts) and
         batch_job['status'] != 'CANCELED'):
    sleep_interval = (30 * (2 ** poll_attempt) +
                      (random.randint(0, 10000) / 1000))
    print ('Batch Job not finished canceling, sleeping for %s seconds.'
           % sleep_interval)
    time.sleep(sleep_interval)
    batch_job = GetBatchJob(client, batch_job['id'])
    poll_attempt += 1

  if batch_job['status'] == 'CANCELED':
    print ('Batch Job with ID "%d" has been successfully canceled.' %
           batch_job['id'])
  else:
    print ('Batch Job with ID "%d" failed to cancel after polling %d times.'
           % (batch_job['id'], max_poll_attempts))


def GetBatchJob(client, batch_job_id):
  """Retrieves the BatchJob with the given id.

  Args:
    client: an instantiated AdWordsClient used to retrieve the BatchJob.
    batch_job_id: a long identifying the BatchJob to be retrieved.
  Returns:
    The BatchJob associated with the given id.
  """
  batch_job_service = client.GetService('BatchJobService', 'v201607')

  selector = {
      'fields': ['Id', 'Status', 'DownloadUrl'],
      'predicates': [
          {
              'field': 'Id',
              'operator': 'EQUALS',
              'values': [batch_job_id]
          }
      ]
  }

  return batch_job_service.get(selector)['entries'][0]


def GetBatchJobDownloadUrlWhenReady(client, batch_job_id,
                                    max_poll_attempts=MAX_POLL_ATTEMPTS):
  """Retrieves the downloadUrl when the BatchJob is complete.

  Args:
    client: an instantiated AdWordsClient used to poll the BatchJob.
    batch_job_id: a long identifying the BatchJob to be polled.
    max_poll_attempts: an int defining the number of times the the BatchJob will
      be checked to determine whether it has completed.

  Returns:
    A str containing the downloadUrl of the completed BatchJob.

  Raises:
    Exception: If the BatchJob hasn't finished after the maximum poll attempts
      have been made.
  """
  batch_job = GetBatchJob(client, batch_job_id)
  if batch_job['status'] == 'CANCELED':
    raise Exception('Batch Job with ID "%s" was canceled before completing.'
                    % batch_job_id)

  poll_attempt = 0

  while (poll_attempt in range(max_poll_attempts) and
         batch_job['status'] in PENDING_STATUSES):
    sleep_interval = (30 * (2 ** poll_attempt) +
                      (random.randint(0, 10000) / 1000))
    print 'Batch Job not ready, sleeping for %s seconds.' % sleep_interval
    time.sleep(sleep_interval)
    batch_job = GetBatchJob(client, batch_job_id)
    poll_attempt += 1

    if 'downloadUrl' in batch_job:
      url = batch_job['downloadUrl']['url']
      print ('Batch Job with Id "%s", Status "%s", and DownloadUrl "%s" ready.'
             % (batch_job['id'], batch_job['status'], url))
      return url

  print ('BatchJob with ID "%s" is being canceled because it was in a pending '
         'state after polling %d times.' % (batch_job_id, max_poll_attempts))
  CancelBatchJob(client, batch_job)


def PrintResponse(batch_job_helper, response_xml):
  """Prints the BatchJobService response.

  Args:
    batch_job_helper: a BatchJobHelper instance.
    response_xml: a string containing a response from the BatchJobService.
  """
  response = batch_job_helper.ParseResponse(response_xml)

  if 'rval' in response['mutateResponse']:
    for data in response['mutateResponse']['rval']:
      if 'errorList' in data:
        print 'Operation %s - FAILURE:' % data['index']
        print '\terrorType=%s' % data['errorList']['errors']['ApiError.Type']
        print '\ttrigger=%s' % data['errorList']['errors']['trigger']
        print '\terrorString=%s' % data['errorList']['errors']['errorString']
        print '\tfieldPath=%s' % data['errorList']['errors']['fieldPath']
        print '\treason=%s' % data['errorList']['errors']['reason']
      if 'result' in data:
        print 'Operation %s - SUCCESS.' % data['index']


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()
  main(adwords_client, ADGROUP_ID)
