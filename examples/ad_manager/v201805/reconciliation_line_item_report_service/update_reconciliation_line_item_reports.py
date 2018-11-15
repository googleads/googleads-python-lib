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

"""This example updates a reconciliation line item report.

To get reconciliation line item reports for a reconciliation report, run
get_reconciliation_line_item_reports_for_reconciliation_report.py
"""

# Import appropriate modules from the client library.
from googleads import ad_manager

# Set the ID of the reconciliation line item report to update.
RECONCILIATION_LINE_ITEM_REPORT_ID = 'INSERT_ID_HERE'


def main(client):
  # Initialize appropriate service.
  reconciliation_line_item_report_service = (client.GetService(
      'ReconciliationLineItemReportService', version='v201805'))

  # Create a statement to select a reconciliation line item report.
  statement = (ad_manager.StatementBuilder(version='v201805')
               .Where('id = :lineItemReportId')
               .OrderBy('id', ascending=True)
               .Limit(1)
               .WithBindVariable('lineItemReportId',
                                 RECONCILIATION_LINE_ITEM_REPORT_ID))

  # Get reconciliation line item reports by statement.
  page = (reconciliation_line_item_report_service
          .getReconciliationLineItemReportsByStatement(statement.ToStatement()))

  line_item_report = page['results'][0]

  # Set and use a manual volume for billing. This example splits the difference
  # between Ad Manager and the third party volume.
  line_item_report['manualVolume'] = (line_item_report['dfpVolume'] +
                                      line_item_report['thirdPartyVolume']) / 2
  line_item_report['reconciliationSource'] = 'MANUAL'

  result = (reconciliation_line_item_report_service
            .updateReconciliationLineItemReports([line_item_report]))

  for updated_report in result:
    print ('Reconciliation line item report with ID %d for line item ID %d was '
           'updated, with manual volume %d' % (updated_report['id'],
                                               updated_report['lineItemId'],
                                               updated_report['manualVolume']))

if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
