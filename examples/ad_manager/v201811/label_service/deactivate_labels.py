#!/usr/bin/env python
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

"""This code example deactivates all active Labels.

To determine which labels exist, run get_all_labels.py. This feature is only
available to Ad Manager 360 solution networks.
"""


# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  # Initialize appropriate service.
  label_service = client.GetService('LabelService', version='v201811')

  # Create query.
  statement = (ad_manager.StatementBuilder(version='v201811')
               .Where('isActive = :isActive')
               .WithBindVariable('isActive', True))

  labels_deactivated = 0

  # Get labels by statement.
  while True:
    response = label_service.getLabelsByStatement(statement.ToStatement())
    if 'results' in response and len(response['results']):
      for label in response['results']:
        print ('Label with id "%s" and name "%s" will be '
               'deactivated.' % (label['id'], label['name']))
      # Perform action.
      result = label_service.performLabelAction(
          {'xsi_type': 'DeactivateLabels'}, statement.ToStatement())
      if result and int(result['numChanges']) > 0:
        labels_deactivated += int(result['numChanges'])
      statement.offset += statement.limit
    else:
      break

  # Display results.
  if labels_deactivated > 0:
    print 'Number of labels deactivated: %s' % labels_deactivated
  else:
    print 'No labels were deactivated.'


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
