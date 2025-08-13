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

"""This example runs a report from a saved query.
"""

# Import appropriate modules from the client library.
import tempfile

from googleads import ad_manager
from googleads import errors

SAVED_QUERY_ID = 'INSERT_SAVED_QUERY_ID_HERE'


def main(client, saved_query_id):
  # Initialize appropriate service.
  report_service = client.GetService('ReportService', version='v202508')

  # Initialize a DataDownloader.
  report_downloader = client.GetDataDownloader(version='v202508')

  # Create statement object to filter for an order.
  statement = (ad_manager.StatementBuilder(version='v202508')
               .Where('id = :id')
               .WithBindVariable('id', int(saved_query_id))
               .Limit(1))

  response = report_service.getSavedQueriesByStatement(
      statement.ToStatement())

  if 'results' in response and len(response['results']):
    saved_query = response['results'][0]

    if saved_query['isCompatibleWithApiVersion']:
      report_job = {}

      # Set report query and optionally modify it.
      report_job['reportQuery'] = saved_query['reportQuery']

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
    else:
      print('The query specified is not compatible with the API version.')


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, SAVED_QUERY_ID)
