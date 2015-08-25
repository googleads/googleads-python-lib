#!/usr/bin/python
#
# Copyright 2014 Google Inc. All Rights Reserved.
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

"""This triggers all workflow external condition requests for a proposal.

Workflow external condition requests must be triggered or skipped for a workflow
to finish. To determine which proposals exist, run get_all_proposals.py.

"""


# Import appropriate modules from the client library.
from googleads import dfp

PROPOSAL_ID = 'INSERT_PROPOSAL_ID_HERE'


def main(client, proposal_id):
  # Initialize appropriate service.
  workflow_request_service = client.GetService('WorkflowRequestService',
                                               version='v201411')

  # Create query.
  values = [
      {
          'key': 'entityId',
          'value': {
              'xsi_type': 'TextValue',
              'value': proposal_id
          }
      },
      {
          'key': 'entityType',
          'value': {
              'xsi_type': 'TextValue',
              'value': 'PROPOSAL'
          }
      },
      {
          'key': 'type',
          'value': {
              'xsi_type': 'TextValue',
              'value': 'WORKFLOW_EXTERNAL_CONDITION_REQUEST'
          }
      }
  ]
  query = ('WHERE entityId = :entityId and entityType = :entityType '
           'and type = :type')

  # Create a filter statement.
  statement = dfp.FilterStatement(query, values)
  workflow_external_condition_requests_triggered = 0

  # Get workflow external condition requests by statement.
  while True:
    response = workflow_request_service.getWorkflowRequestsByStatement(
        statement.ToStatement())
    if 'results' in response:
      # Display results.
      for workflow_request in response['results']:
        print ('Workflow external condition request with id \'%s\' for %s '
               'with id \'%s\' will be triggered.' %
               (workflow_request['id'],
                workflow_request['entityType'],
                workflow_request['entityId']))
      # Perform action.
      result = workflow_request_service.performWorkflowRequestAction(
          {'xsi_type': 'TriggerWorkflowExternalConditionRequests'},
          statement.ToStatement())
      if result and int(result['numChanges']) > 0:
        workflow_external_condition_requests_triggered += int(
            result['numChanges'])
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  # Display results.
  if workflow_external_condition_requests_triggered > 0:
    print ('\nNumber of workflow external condition requests triggered: %s' %
           workflow_external_condition_requests_triggered)
  else:
    print '\nNo workflow external condition requests were triggered.'

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, PROPOSAL_ID)
