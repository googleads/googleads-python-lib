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

"""Runs a report equal to the "Whole network report" on the DFP website."""

import tempfile

# Import appropriate modules from the client library.
from googleads import dfp
from googleads import errors


def main(client):
  # Initialize appropriate service.
  network_service = client.GetService('NetworkService', version='v201705')
  # Initialize a DataDownloader.
  report_downloader = client.GetDataDownloader(version='v201705')

  # Get root ad unit id for network.
  root_ad_unit_id = (
      network_service.getCurrentNetwork()['effectiveRootAdUnitId'])

  # Set filter statement and bind value for reportQuery.
  values = [{
      'key': 'parent_ad_unit_id',
      'value': {
          'xsi_type': 'NumberValue',
          'value': root_ad_unit_id
      }
  }]
  filter_statement = {'query': 'WHERE PARENT_AD_UNIT_ID = :parent_ad_unit_id',
                      'values': values}

  # Create report job.
  report_job = {
      'reportQuery': {
          'dimensions': ['DATE', 'AD_UNIT_NAME'],
          'adUnitView': 'HIERARCHICAL',
          'columns': ['AD_SERVER_IMPRESSIONS', 'AD_SERVER_CLICKS',
                      'DYNAMIC_ALLOCATION_INVENTORY_LEVEL_IMPRESSIONS',
                      'DYNAMIC_ALLOCATION_INVENTORY_LEVEL_CLICKS',
                      'TOTAL_INVENTORY_LEVEL_IMPRESSIONS',
                      'TOTAL_INVENTORY_LEVEL_CPM_AND_CPC_REVENUE'],
          'dateRangeType': 'LAST_WEEK',
          'statement': filter_statement
      }
  }

  try:
    # Run the report and wait for it to finish.
    report_job_id = report_downloader.WaitForReport(report_job)
  except errors.DfpReportError, e:
    print 'Failed to generate report. Error was: %s' % e

  # Change to your preferred export format.
  export_format = 'CSV_DUMP'

  report_file = tempfile.NamedTemporaryFile(suffix='.csv.gz', delete=False)

  # Download report data.
  report_downloader.DownloadReportToFile(
      report_job_id, export_format, report_file)

  report_file.close()

  # Display results.
  print 'Report job with id "%s" downloaded to:\n%s' % (
      report_job_id, report_file.name)

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
