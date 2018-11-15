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
"""This example gets workflow approval requests.

Workflow approval requests must be approved or rejected for a workflow to
finish.
"""

# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  # Initialize appropriate service.
  workflow_request_service = client.GetService(
      'WorkflowRequestService', version='v201805')
  # Create a statement to select workflow requests.
  statement = (ad_manager.StatementBuilder(version='v201805')
               .Where('type = :type')
               .WithBindVariable('type', 'WORKFLOW_APPROVAL_REQUEST'))

  # Retrieve a small amount of workflow requests at a time, paging
  # through until all workflow requests have been retrieved.
  while True:
    response = workflow_request_service.getWorkflowRequestsByStatement(
        statement.ToStatement())
    if 'results' in response and len(response['results']):
      for workflow_request in response['results']:
        # Print out some information for each workflow request.
        print('Workflow request with ID "%d", entity type "%s", and entity ID '
              '"%d" was found.\n' % (workflow_request['id'],
                                     workflow_request['entityType'],
                                     workflow_request['entityId']))
      statement.offset += statement.limit
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
