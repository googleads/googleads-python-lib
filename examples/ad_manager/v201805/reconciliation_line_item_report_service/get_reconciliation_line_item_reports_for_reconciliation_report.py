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

"""This example gets all line item reports for a given reconciliation report.

To determine how many reconciliation reports exist,
run get_all_reconciliation_reports.py.
"""

# Import appropriate modules from the client library.
from googleads import ad_manager

# Set the ID of the reconciliation report to query.
RECONCILIATION_REPORT_ID = 'INSERT_RECONCILIATION_REPORT_ID_HERE'


def main(client):
  # Initialize appropriate service.
  reconciliation_line_item_report_service = (client.GetService(
      'ReconciliationLineItemReportService', version='v201805'))

  # Create a statement to select reconciliation line item reports.
  statement = (ad_manager.StatementBuilder(version='v201805')
               .Where(('reconciliationReportId = :reconciliationReportId AND '
                       'lineItemId != :lineItemId'))
               .OrderBy('lineItemId', ascending=True)
               .WithBindVariable('reconciliationReportId',
                                 RECONCILIATION_REPORT_ID)
               .WithBindVariable('lineItemId', 0))

  # Retrieve a small amount of reconciliation line item reports at a time,
  # paging through until all reconciliation line item reports have been
  # retrieved.
  result_set_size = 0
  should_continue = True

  while should_continue:
    page = (reconciliation_line_item_report_service
            .getReconciliationLineItemReportsByStatement(
                statement.ToStatement()))
    if 'results' in page and len(page['results']):
      result_set_size += page['totalResultSetSize']
      # Iterate over individual results in the page.
      for line_item_report in page['results']:
        print ('Reconciliation line item report with ID %d, line item ID %d, '
               'reconciliation source "%s", and reconciled volume %d was '
               'found.' % (line_item_report['id'],
                           line_item_report['lineItemId'],
                           line_item_report['reconciliationSource'],
                           (line_item_report['reconciledVolume']
                            if 'reconciledVolume' in line_item_report else 0)))
    # Update statement for next page.
    statement.offset += statement.limit
    should_continue = statement.offset < result_set_size

  print 'Number of results found: %d' % result_set_size


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
