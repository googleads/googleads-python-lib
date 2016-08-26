#!/usr/bin/python
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
"""This example gets the previous billing period's reconciliation report.
"""

# Import appropriate modules from the client library.
from datetime import date
from datetime import timedelta

from googleads import dfp


def main(client):
  # Initialize appropriate service.
  reconciliation_report_service = client.GetService(
      'ReconciliationReportService', version='v201608')

  first_of_the_month = date.today().replace(day=1)
  last_month = first_of_the_month - timedelta(days=1)

  query = 'WHERE startDate = :startDate'
  values = [
      {'key': 'startDate',
       'value': {
           'xsi_type': 'TextValue',
           'value': last_month.strftime('%Y-%m-01')
       }},
  ]
  # Create a statement to select reconciliation reports.
  statement = dfp.FilterStatement(query, values)

  # Retrieve a small amount of reconciliation reports at a time, paging
  # through until all reconciliation reports have been retrieved.
  while True:
    response = reconciliation_report_service.getReconciliationReportsByStatement(
        statement.ToStatement())
    if 'results' in response:
      for reconciliation_report in response['results']:
        # Print out some information for each reconciliation report.
        print(
            'Reconciliation report with ID "%d" and start date "%s" was found.'
            '\n' % (reconciliation_report['id'],
                    last_month.strftime('%Y-%m-01')))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
