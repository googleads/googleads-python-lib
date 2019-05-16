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

"""This code example deactivates a creative wrapper belonging to a label.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import ad_manager

LABEL_ID = 'INSERT_LABEL_ID_HERE'


def main(client, label_id):
  # Initialize appropriate service.
  creative_wrapper_service = client.GetService('CreativeWrapperService',
                                               version='v201905')

  # Create a query to select the active creative wrappers for the given label.
  statement = (ad_manager.StatementBuilder(version='v201905')
               .Where('status = :status AND labelId = :labelId')
               .WithBindVariable('status', 'ACTIVE')
               .WithBindVariable('labelId', long(label_id)))

  creative_wrappers_deactivated = 0

  # Get creative wrappers by statement.
  while True:
    response = creative_wrapper_service.getCreativeWrappersByStatement(
        statement.ToStatement())
    if 'results' in response and len(response['results']):
      # Display results.
      for creative_wrapper in response['results']:
        print ('Creative wrapper with ID "%s" applying to label "%s" with '
               'status "%s" will be deactivated.' %
               (creative_wrapper['id'],
                creative_wrapper['labelId'],
                creative_wrapper['status']))
      # Perform action.
      result = creative_wrapper_service.performCreativeWrapperAction(
          {'xsi_type': 'DeactivateCreativeWrappers'}, statement.ToStatement())
      if result and int(result['numChanges']) > 0:
        creative_wrappers_deactivated += int(result['numChanges'])
      statement.offset += statement.limit
    else:
      break

  # Display results.
  if creative_wrappers_deactivated > 0:
    print ('Number of creative wrappers deactivated: %s' %
           creative_wrappers_deactivated)
  else:
    print 'No creative wrappers were deactivated.'


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, LABEL_ID)
