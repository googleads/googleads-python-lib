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

"""Gets a reconciliation report's rows for line items that Ad Manager served.
"""

# Import appropriate modules from the client library.
from googleads import ad_manager

# Set the ID of the reconciliation report row.
RECONCILIATION_REPORT_ID = 'INSERT_RECONCILIATION_REPORT_ID_HERE'


def main(client, reconciliation_report_id):
  # Initialize appropriate service.
  reconciliation_report_row_service = client.GetService(
      'ReconciliationReportRowService', version='v201802')

  # Create a statement to select reconciliation report rows.
  statement = (ad_manager.StatementBuilder()
               .Where(('reconciliationReportId = :reportId '
                       'AND lineItemId != :lineItemId'))
               .WithBindVariable('lineItemId', 0)
               .WithBindVariable('reportId', long(reconciliation_report_id)))

  # Retrieve a small amount of reconciliation report rows at a time, paging
  # through until all reconciliation report rows have been retrieved.
  while True:
    response = (
        reconciliation_report_row_service
        .getReconciliationReportRowsByStatement(
            statement.ToStatement()))
    if 'results' in response and len(response['results']):
      for reconciliation_report_row in response['results']:
        # Print out some information for each reconciliation report row.
        print('Reconciliation report row with ID "%d", reconciliation source '
              '"%s", and reconciled volume "%d" was found.\n' %
              (reconciliation_report_row['id'],
               reconciliation_report_row['reconciliationSource'],
               reconciliation_report_row['reconciledVolume']))
      statement.offset += statement.limit
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, RECONCILIATION_REPORT_ID)
