#!/usr/bin/env python
#
# Copyright 2017 Google Inc. All Rights Reserved.
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

"""Runs a report for LineItems with additional data from a PQL table.

Fetches a basic report over a network's LineItems and then adds some
extra columns which might be useful for future analysis, such as
LineItemType, from the PQL Line_Item table, creating a match table.
"""

from datetime import date
from datetime import timedelta
import tempfile

# Import appropriate modules from the client library.
from googleads import ad_manager
from googleads import errors

try:
  import pandas
except ImportError:
  raise ImportError('This example requires the pandas library to be installed.')


def main(client):
  # Set the start and end dates of the report to run (past 8 days).
  end_date = date.today()
  start_date = end_date - timedelta(days=8)

  # Create report job.
  report_job = {
      'reportQuery': {
          'dimensions': ['LINE_ITEM_ID', 'LINE_ITEM_NAME'],
          'columns': ['AD_SERVER_IMPRESSIONS', 'AD_SERVER_CLICKS',
                      'AD_SERVER_CTR', 'AD_SERVER_CPM_AND_CPC_REVENUE',
                      'AD_SERVER_WITHOUT_CPD_AVERAGE_ECPM'],
          'dateRangeType': 'CUSTOM_DATE',
          'startDate': start_date,
          'endDate': end_date
      }
  }

  # Initialize a DataDownloader.
  report_downloader = client.GetDataDownloader(version='v201902')

  try:
    # Run the report and wait for it to finish.
    report_job_id = report_downloader.WaitForReport(report_job)
  except errors.AdManagerReportError as e:
    print('Failed to generate report. Error was: %s' % e)

  with tempfile.NamedTemporaryFile(
      suffix='.csv.gz', mode='wb', delete=False) as report_file:
    # Download report data.
    report_downloader.DownloadReportToFile(
        report_job_id, 'CSV_DUMP', report_file)

  # Create a PQL query to fetch the line item data
  line_items_pql_query = ('SELECT Id, LineItemType, Status FROM LineItem')

  # Download the response from PQL select statement
  line_items = report_downloader.DownloadPqlResultToList(line_items_pql_query)

  # Use pandas to join the two csv files into a match table
  report = pandas.read_csv(report_file.name)
  line_items = pandas.DataFrame(data=line_items[1:], columns=line_items[0])
  merged_result = pandas.merge(report, line_items,
                               left_on='Dimension.LINE_ITEM_ID', right_on='id')
  merged_result.to_csv('~/complete_line_items_report.csv', index=False)


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
