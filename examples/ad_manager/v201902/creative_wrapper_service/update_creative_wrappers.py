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

"""This code example updates a creative wrapper to the 'OUTER' wrapping order.

To determine which creative wrappers exist, run get_all_creative_wrappers.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import ad_manager

# Set the ID of the creative wrapper to update.
CREATIVE_WRAPPER_ID = 'INSERT_CREATIVE_WRAPPER_ID_HERE'


def main(client, creative_wrapper_id):
  # Initialize appropriate service.
  creative_wrapper_service = client.GetService('CreativeWrapperService',
                                               version='v201902')

  # Create statement to get a creative wrapper by ID.
  statement = (ad_manager.StatementBuilder(version='v201902')
               .Where('id = :creativeWrapperId')
               .WithBindVariable('creativeWrapperId',
                                 long(creative_wrapper_id)))

  # Get creative wrappers.
  response = creative_wrapper_service.getCreativeWrappersByStatement(
      statement.ToStatement())

  if 'results' in response and len(response['results']):
    updated_creative_wrappers = []
    for creative_wrapper in response['results']:
      creative_wrapper['ordering'] = 'OUTER'
      updated_creative_wrappers.append(creative_wrapper)

    # Update the creative wrappers on the server.
    creative_wrappers = creative_wrapper_service.updateCreativeWrappers(
        updated_creative_wrappers)

    # Display results.
    for creative_wrapper in creative_wrappers:
      print (('Creative wrapper with ID "%s" and wrapping order "%s" '
              'was updated.') % (creative_wrapper['id'],
                                 creative_wrapper['ordering']))
  else:
    print 'No creative wrappers found to update.'


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, CREATIVE_WRAPPER_ID)
