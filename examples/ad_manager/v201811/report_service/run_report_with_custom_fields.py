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

# Set the ID of the order to get line items from.
ORDER_ID = 'INSERT_ORDER_ID_HERE'


def main(client, order_id):
  # Initialize appropriate service.
  line_item_service = client.GetService('LineItemService', version='v201811')
  # Initialize a DataDownloader.
  report_downloader = client.GetDataDownloader(version='v201811')

  # Filter for line items of a given order.
  statement = (ad_manager.StatementBuilder(version='v201811')
               .Where('orderId = :orderId')
               .WithBindVariable('orderId', long(order_id)))

  # Collect all line item custom field IDs for an order.
  custom_field_ids = set()

  # Get users by statement.
  while True:
    response = line_item_service.getLineItemsByStatement(
        statement.ToStatement())
    if 'results' in response and len(response['results']):
      # Get custom field IDs from the line items of an order.
      for line_item in response['results']:
        if 'customFieldValues' in line_item:
          for custom_field_value in line_item['customFieldValues']:
            custom_field_ids.add(custom_field_value['customFieldId'])
      statement.offset += statement.limit
    else:
      break

  # Modify statement for reports
  statement.limit = None
  statement.offset = None
  statement.Where('ORDER_ID = :orderId')

  # Create report job.
  report_job = {
      'reportQuery': {
          'dimensions': ['LINE_ITEM_ID', 'LINE_ITEM_NAME'],
          'statement': statement.ToStatement(),
          'columns': ['AD_SERVER_IMPRESSIONS'],
          'dateRangeType': 'LAST_MONTH',
          'customFieldIds': list(custom_field_ids)
      }
  }

  try:
    # Run the report and wait for it to finish.
    report_job_id = report_downloader.WaitForReport(report_job)
  except errors.AdManagerReportError, e:
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
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, ORDER_ID)
