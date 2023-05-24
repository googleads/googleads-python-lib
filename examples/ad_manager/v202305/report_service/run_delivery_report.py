#!/usr/bin/env python
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

"""Runs a report similar to the "Orders report" on the Ad Manager website.

Includes additional attributes and can filter to include just one order.
"""

from datetime import datetime
from datetime import timedelta
import tempfile

# Import appropriate modules from the client library.
from googleads import ad_manager
from googleads import errors

ORDER_ID = 'INSERT_ORDER_ID_HERE'


def main(client, order_id):
  # Create statement object to filter for an order.
  statement = (ad_manager.StatementBuilder(version='v202305')
               .Where('ORDER_ID = :id')
               .WithBindVariable('id', int(order_id))
               .Limit(None)  # No limit or offset for reports
               .Offset(None))

  # Set the start and end dates of the report to run (past 8 days).
  end_date = datetime.now().date()
  start_date = end_date - timedelta(days=8)

  # Create report job.
  report_job = {
      'reportQuery': {
          'dimensions': ['ORDER_ID', 'ORDER_NAME'],
          'dimensionAttributes': ['ORDER_TRAFFICKER', 'ORDER_START_DATE_TIME',
                                  'ORDER_END_DATE_TIME'],
          'statement': statement.ToStatement(),
          'columns': ['AD_SERVER_IMPRESSIONS', 'AD_SERVER_CLICKS',
                      'AD_SERVER_CTR', 'AD_SERVER_CPM_AND_CPC_REVENUE',
                      'AD_SERVER_WITHOUT_CPD_AVERAGE_ECPM'],
          'dateRangeType': 'CUSTOM_DATE',
          'startDate': start_date,
          'endDate': end_date
      }
  }

  # Initialize a DataDownloader.
  report_downloader = client.GetDataDownloader(version='v202305')

  try:
    # Run the report and wait for it to finish.
    report_job_id = report_downloader.WaitForReport(report_job)
  except errors.AdManagerReportError as e:
    print('Failed to generate report. Error was: %s' % e)

  # Change to your preferred export format.
  export_format = 'CSV_DUMP'

  report_file = tempfile.NamedTemporaryFile(suffix='.csv.gz', delete=False)

  # Download report data.
  report_downloader.DownloadReportToFile(
      report_job_id, export_format, report_file)

  report_file.close()

  # Display results.
  print('Report job with id "%s" downloaded to:\n%s' % (
      report_job_id, report_file.name))

if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, ORDER_ID)
