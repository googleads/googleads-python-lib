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

"""This example downloads an adgroup performance report for all child accounts.

To get report fields, run get_report_fields.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.
"""

import multiprocessing
import os
from Queue import Empty
import time

import googleads.adwords
import googleads.errors

# Timeout between retries in seconds.
BACKOFF_FACTOR = 5
# Maximum number of processes to spawn.
MAX_PROCESSES = multiprocessing.cpu_count()
# Maximum number of retries for 500 errors.
MAX_RETRIES = 5
# Maximum number of items to be sent in a single API response.
PAGE_SIZE = 100
# Directory to download the reports to.
REPORT_DOWNLOAD_DIRECTORY = 'INSERT_REPORT_DOWNLOAD_DIRECTORY'


def _DownloadReport(process_id, report_download_directory, customer_id,
                    report_definition):
  """Helper function used by ReportWorker to download customer report.

  Note that multiprocessing differs between Windows / Unix environments. A
  Process or its subclasses in Windows must be serializable with pickle, but
  that is not possible for AdWordsClient or ReportDownloader. This top-level
  function is used as a work-around for Windows support.

  Args:
    process_id: The PID of the process downloading the report.
    report_download_directory: A string indicating the directory where you
        would like to download the reports.
    customer_id: A str AdWords customer ID for which the report is being
        downloaded.
    report_definition: A dict containing the report definition to be used.

  Returns:
    A tuple indicating a boolean success/failure status, and dict request
    context.
  """
  report_downloader = (googleads.adwords.AdWordsClient.LoadFromStorage()
                       .GetReportDownloader())

  filepath = os.path.join(report_download_directory,
                          'adgroup_%d.csv' % customer_id)
  retry_count = 0

  while True:
    print ('[%d/%d] Loading report for customer ID "%s" into "%s"...'
           % (process_id, retry_count, customer_id, filepath))
    try:
      with open(filepath, 'wb') as handler:
        report_downloader.DownloadReport(
            report_definition, output=handler,
            client_customer_id=customer_id)
      return (True, {'customerId': customer_id})
    except googleads.errors.AdWordsReportError as e:
      if e.code == 500 and retry_count < MAX_RETRIES:
        time.sleep(retry_count * BACKOFF_FACTOR)
      else:
        print ('Report failed for customer ID "%s" with code "%d" after "%d" '
               'retries.' % (customer_id, e.code, retry_count+1))
        return (False, {'customerId': customer_id, 'code': e.code,
                        'message': e.message})


class ReportWorker(multiprocessing.Process):
  """A worker Process used to download reports for a set of customer IDs."""

  def __init__(self, report_download_directory, report_definition,
               input_queue, success_queue, failure_queue):
    """Initializes a ReportWorker.

    Args:
      report_download_directory: A string indicating the directory where you
        would like to download the reports.
      report_definition: A dict containing the report definition that you would
        like to run against all customer IDs in the input_queue.
      input_queue: A Queue instance containing all of the customer IDs that
        the report_definition will be run against.
      success_queue: A Queue instance that the details of successful report
        downloads will be saved to.
      failure_queue: A Queue instance that the details of failed report
        downloads will be saved to.
    """
    super(ReportWorker, self).__init__()
    self.report_download_directory = report_download_directory
    self.report_definition = report_definition
    self.input_queue = input_queue
    self.success_queue = success_queue
    self.failure_queue = failure_queue

  def run(self):
    while True:
      try:
        customer_id = self.input_queue.get(timeout=0.01)
      except Empty:
        break
      result = _DownloadReport(self.ident, self.report_download_directory,
                               customer_id, self.report_definition)
      (self.success_queue if result[0] else self.failure_queue).put(result[1])


def GetCustomerIDs(client):
  """Retrieves all CustomerIds in the account hierarchy.

  Note that your configuration file must specify a client_customer_id belonging
  to an AdWords manager account.

  Args:
    client: an AdWordsClient instance.
  Raises:
    Exception: if no CustomerIds could be found.
  Returns:
    A Queue instance containing all CustomerIds in the account hierarchy.
  """
  # For this example, we will use ManagedCustomerService to get all IDs in
  # hierarchy that do not belong to MCC accounts.
  managed_customer_service = client.GetService('ManagedCustomerService',
                                               version='v201710')

  offset = 0

  # Get the account hierarchy for this account.
  selector = {
      'fields': ['CustomerId'],
      'predicates': [{
          'field': 'CanManageClients',
          'operator': 'EQUALS',
          'values': [False]
      }],
      'paging': {
          'startIndex': str(offset),
          'numberResults': str(PAGE_SIZE)
      }
  }

  # Using Queue to balance load between processes.
  queue = multiprocessing.Queue()
  more_pages = True

  while more_pages:
    page = managed_customer_service.get(selector)

    if page and 'entries' in page and page['entries']:
      for entry in page['entries']:
        queue.put(entry['customerId'])
    else:
      raise Exception('Can\'t retrieve any customer ID.')
    offset += PAGE_SIZE
    selector['paging']['startIndex'] = str(offset)
    more_pages = offset < int(page['totalNumEntries'])

  return queue


def main(client, report_download_directory):
  # Determine list of customer IDs to retrieve report for.
  input_queue = GetCustomerIDs(client)
  reports_succeeded = multiprocessing.Queue()
  reports_failed = multiprocessing.Queue()

  # Create report definition.
  report_definition = {
      'reportName': 'Custom ADGROUP_PERFORMANCE_REPORT',
      'dateRangeType': 'LAST_7_DAYS',
      'reportType': 'ADGROUP_PERFORMANCE_REPORT',
      'downloadFormat': 'CSV',
      'selector': {
          'fields': ['CampaignId', 'AdGroupId', 'Impressions', 'Clicks',
                     'Cost'],
          # Predicates are optional.
          'predicates': {
              'field': 'AdGroupStatus',
              'operator': 'IN',
              'values': ['ENABLED', 'PAUSED']
          }
      },
  }

  queue_size = input_queue.qsize()
  num_processes = min(queue_size, MAX_PROCESSES)
  print 'Retrieving %d reports with %d processes:' % (queue_size, num_processes)

  # Start all the processes.
  processes = [ReportWorker(report_download_directory,
                            report_definition, input_queue, reports_succeeded,
                            reports_failed)
               for _ in range(num_processes)]

  for process in processes:
    process.start()

  for process in processes:
    process.join()

  print 'Finished downloading reports with the following results:'
  while True:
    try:
      success = reports_succeeded.get(timeout=0.01)
    except Empty:
      break
    print '\tReport for CustomerId "%d" succeeded.' % success['customerId']

  while True:
    try:
      failure = reports_failed.get(timeout=0.01)
    except Empty:
      break
    print ('\tReport for CustomerId "%d" failed with error code "%s" and '
           'message: %s.' % (failure['customerId'], failure['code'],
                             failure['message']))


if __name__ == '__main__':
  adwords_client = googleads.adwords.AdWordsClient.LoadFromStorage()
  main(adwords_client, REPORT_DOWNLOAD_DIRECTORY)
