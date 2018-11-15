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

"""This example submits a reconciliation order report.

To get all reconciliation order reports for a reconciliation report,
run get get_reconciliation_order_reports_for_reconciliation_report.py.
"""

# Import appropriate modules from the client library.
from googleads import ad_manager

# Set the ID of the reconciliation order report to submit.
RECONCILIATION_ORDER_REPORT_ID = 'INSERT_ID_HERE'


def main(client):
  # Initialize appropriate service.
  reconciliation_order_report_service = (client.GetService(
      'ReconciliationOrderReportService', version='v201808'))

  # Create a statement to select reconciliation order reports.
  statement = (ad_manager.StatementBuilder(version='v201808')
               .Where('id = :id')
               .OrderBy('id', ascending=True)
               .Limit(1)
               .WithBindVariable('id', RECONCILIATION_ORDER_REPORT_ID))

  # Get reconciliation order reports by statement.
  page = (reconciliation_order_report_service
          .getReconciliationOrderReportsByStatement(statement.ToStatement()))

  report = page['results'][0]

  print ('Reconciliation order report with ID %d will be submitted.' %
         report['id'])

  # Remove limit and offset from statement.
  statement.limit = None
  statement.offset = None

  # Perform action.
  result = (reconciliation_order_report_service
            .performReconciliationOrderReportAction(
                {'xsi_type': 'SubmitReconciliationOrderReports'},
                statement.ToStatement()))

  if result and result['numChanges'] > 0:
    print ('Number of reconciliation order reports submitted: %d' %
           result['numChanges'])
  else:
    print 'No reconciliation order reports were submitted.'


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
