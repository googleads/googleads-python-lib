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

"""Runs a report with custom fields found in the line items of an order."""

import tempfile

# Import appropriate modules from the client library.
from googleads import ad_manager
from googleads import errors

CUSTOM_FIELD_ID = 'INSERT_CUSTOM_FIELD_ID'
CUSTOM_DIMENSION_KEY_ID = 'INSERT_CUSTOM_DIMENSION_KEY_ID'


def main(client, custom_field_id, custom_dimension_key_id):
  # Initialize a DataDownloader.
  report_downloader = client.GetDataDownloader(version='v202502')

  # Create report job.
  report_job = {
      'reportQuery': {
          'dimensions': ['CUSTOM_DIMENSION', 'LINE_ITEM_ID', 'LINE_ITEM_NAME'],
          'columns': ['AD_SERVER_IMPRESSIONS'],
          'dateRangeType': 'LAST_MONTH',
          'customFieldIds': [custom_field_id],
          'customDimensionKeyIds': [custom_dimension_key_id]
      }
  }

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
  main(ad_manager_client, CUSTOM_FIELD_ID, CUSTOM_DIMENSION_KEY_ID)
