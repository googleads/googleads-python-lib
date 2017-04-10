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

"""This example retrieves the report download stream.

To get report fields, run get_report_fields.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


import logging
import StringIO
import sys
from googleads import adwords


logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.transport').setLevel(logging.DEBUG)

# The chunk size used for the report download.
CHUNK_SIZE = 16 * 1024


def main(client):
  report_downloader = client.GetReportDownloader(version='v201702')

  # Create report definition.
  report = {
      'reportName': 'Last 7 days CRITERIA_PERFORMANCE_REPORT',
      'dateRangeType': 'LAST_7_DAYS',
      'reportType': 'CRITERIA_PERFORMANCE_REPORT',
      'downloadFormat': 'CSV',
      'selector': {
          'fields': ['CampaignId', 'AdGroupId', 'Id', 'CriteriaType',
                     'Criteria', 'FinalUrls', 'Impressions', 'Clicks', 'Cost']
      }
  }

  # Retrieve the report stream and print it out
  report_data = StringIO.StringIO()
  stream_data = report_downloader.DownloadReportAsStream(
      report, skip_report_header=False, skip_column_header=False,
      skip_report_summary=False, include_zero_impressions=True)

  try:
    while True:
      chunk = stream_data.read(CHUNK_SIZE)
      if not chunk: break
      report_data.write(chunk.decode() if sys.version_info[0] == 3
                        and getattr(report_data, 'mode', 'w') == 'w' else chunk)
    print report_data.getvalue()
  finally:
    report_data.close()
    stream_data.close()


if __name__ == '__main__':
  adwords_client = adwords.AdWordsClient.LoadFromStorage()
  main(adwords_client)
