#!/usr/bin/env python
#
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This example streams the results of an ad hoc report.

Collects total impressions by campaign from each line. Demonstrates how you can
extract data from a large report without holding the entire result set in
memory or using files.
"""

import collections

from googleads import adwords


def main(client):
  # Initialize appropriate service.
  report_downloader = client.GetReportDownloader(version='v201809')

  # Create report query.
  report_query = (adwords.ReportQueryBuilder()
                  .Select('Id', 'AdNetworkType1', 'Impressions')
                  .From('CRITERIA_PERFORMANCE_REPORT')
                  .Where('Status').In('ENABLED', 'PAUSED')
                  .During('LAST_7_DAYS')
                  .Build())

  # Retrieve the report stream.
  stream = report_downloader.DownloadReportAsStreamWithAwql(
      report_query, 'CSV', skip_report_header=True, skip_column_header=True,
      skip_report_summary=True, include_zero_impressions=True)

  ad_network_map = collections.defaultdict(int)

  try:
    while True:
      line = stream.readline()
      if not line: break
      process_line(line, ad_network_map=ad_network_map)
  finally:
    stream.close()

  print('Total impressions by ad network type 1:')
  for ad_network_type, impressions in sorted(ad_network_map.iteritems()):
    print('%s: %s' % (ad_network_type, impressions))


def process_line(line, ad_network_map):
  _, ad_network_type_1, impressions = line.split(',')
  ad_network_map[ad_network_type_1] += int(impressions)


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client)
