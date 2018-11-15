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

"""This example updates a reconciliation report row.

To determine which reconciliation report rows exist,
run get_reconciliation_report_rows_for_reconciliation_report.py
"""

# Import appropriate modules from the client library.
from googleads import ad_manager

# Set the ID of the reconciliation report row.
RECONCILIATION_REPORT_ROW_ID = 'INSERT_ID_HERE'

# Set the ID of the reconciliation report.
RECONCILIATION_REPORT_ID = 'INSERT_RECONCILIATION_REPORT_ID_HERE'


def main(client):
  # Initialize appropriate service.
  reconciliation_report_row_service = (client.GetService(
      'ReconciliationReportRowService', version='v201805'))

  # Create a statement to select reconciliation report rows.
  statement = (ad_manager.StatementBuilder(version='v201805')
               .Where(('id = :reconciliationReportRowId AND '
                       'reconciliationReportId = :reconciliationReportId'))
               .OrderBy('id', ascending=True)
               .WithBindVariable('reconciliationReportRowId',
                                 RECONCILIATION_REPORT_ROW_ID)
               .WithBindVariable('reconciliationReportId',
                                 RECONCILIATION_REPORT_ID))

  # Get reconciliation report rows by statement.
  page = (reconciliation_report_row_service
          .getReconciliationReportRowsByStatement(statement.ToStatement()))

  row = page['results'][0]

  # Set a comment on the reconciliation report row.
  row['comments'] = ('Third part volume didn\'t match DFP - we agreed to split '
                     'the difference')

  # Set and use a manual volume for billing.
  row['manualVolume'] = (row['dfpVolume'] + row['thirdPartyVolume']) / 2
  row['reconciliationSource'] = 'MANUAL'

  updated_rows = (reconciliation_report_row_service
                  .updateReconciliationReportRows([row]))

  for updated_row in updated_rows:
    print ('Reconciliation report row for line item ID %d and creative ID %d '
           'was updated, with manual volume %d' % (updated_row['lineItemId'],
                                                   updated_row['creativeId'],
                                                   updated_row['manualVolume']))


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
