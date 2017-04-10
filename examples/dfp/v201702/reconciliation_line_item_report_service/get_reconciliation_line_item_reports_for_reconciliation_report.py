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
"""Gets a reconciliation report's data for line items that served through DFP.
"""

# Import appropriate modules from the client library.
from googleads import dfp

RECONCILIATION_REPORT_ID = 'INSERT_RECONCILIATION_REPORT_ID_HERE'


def main(client, reconciliation_report_id):
  # Initialize appropriate service.
  reconciliation_line_item_report_service = client.GetService(
      'ReconciliationLineItemReportService', version='v201702')
  query = ('WHERE reconciliationReportId = :reconciliationReportId AND '
           'lineItemId != :lineItemId')
  values = [
      {'key': 'reconciliationReportId',
       'value': {
           'xsi_type': 'TextValue',
           'value': reconciliation_report_id
       }},
      {'key': 'lineItemId',
       'value': {
           'xsi_type': 'NumberValue',
           'value': '0'
       }},
  ]
  # Create a statement to select reconciliation line item reports.
  statement = dfp.FilterStatement(query, values)

  # Retrieve a small amount of reconciliation line item reports at a time,
  # paging through until all reconciliation line item reports have been
  # retrieved.
  while True:
    response = (
        reconciliation_line_item_report_service
        .getReconciliationLineItemReportsByStatement(
            statement.ToStatement()))
    if 'results' in response:
      for reconciliation_line_item_report in response['results']:
        # Print out some information for each reconciliation line item report.
        print(
            'Reconciliation line item report with ID "%d", line item ID "%d", '
            'reconciliation source "%s", and reconciled volume "%d" was '
            'found.\n' %
            (reconciliation_line_item_report['id'],
             reconciliation_line_item_report['lineItemId'],
             reconciliation_line_item_report['reconciliationSource'],
             reconciliation_line_item_report['reconciledVolume']))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, RECONCILIATION_REPORT_ID)
