#!/usr/bin/python
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

"""This example gets workflow external condition requests.

Workflow external condition requests must be triggered or skipped for a workflow
to finish.

Tags: WorkflowRequestService.getWorkflowRequestsByStatement
"""

__author__ = 'Nicholas Chen'

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  workflow_request_service = client.GetService('WorkflowRequestService',
                                               version='v201505')

  # Create statement object to select a single proposal by an ID.
  values = [{
      'key': 'type',
      'value': {
          'xsi_type': 'TextValue',
          'value': 'WORKFLOW_EXTERNAL_CONDITION_REQUEST'
      }
  }]
  query = 'WHERE type = :type'

  statement = dfp.FilterStatement(query, values)

  # Get proposals by statement.
  while True:
    response = workflow_request_service.getWorkflowRequestsByStatement(
        statement.ToStatement())
    if 'results' in response:
      # Display results.
      for workflow_request in response['results']:
        print ('Workflow external condition request with id \'%s\' for %s '
               'with id \'%s\' was found.' % (workflow_request['id'],
                                              workflow_request['entityType'],
                                              workflow_request['entityId']))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
