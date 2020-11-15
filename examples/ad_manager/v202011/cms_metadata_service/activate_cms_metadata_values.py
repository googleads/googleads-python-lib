#!/usr/bin/env python
#
# Copyright 2020 Google LLC
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

"""This example activates CMS Metadata Values for a particular CMS Metadata Key.
"""

# Import appropriate modules from the client library.
from googleads import ad_manager

# Set the id of the CMS Metadata Key on which to activate the CMS Metadata
# Values.
CMS_METADATA_KEY_ID = 'INSERT_CMS_METADATA_KEY_ID_HERE'


def main(client, cms_metadata_key_id):
  # Initialize appropriate service.
  cms_metadata_service = client.GetService('CmsMetadataService',
                                           version='v202011')

  # Create query.
  statement = (ad_manager.StatementBuilder(version='v202011')
               .Where('cmsKeyId = :cmsKeyId AND status = :status')
               .WithBindVariable('status', 'INACTIVE')
               .WithBindVariable('cmsKeyId', int(cms_metadata_key_id)))

  values_activated = 0

  # Get CMS Metadata Values by statement.
  while True:
    response = cms_metadata_service.getCmsMetadataValuesByStatement(
        statement.ToStatement())
    if 'results' in response and len(response['results']):
      for cms_metadata_value in response['results']:
        print('CMS Metadata Value with id "%s" and name "%s" will be '
              'activated.' % (cms_metadata_value['cmsMetadataValueId'],
                              cms_metadata_value['valueName']))

      # Perform action.
      result = cms_metadata_service.performCmsMetadataValueAction(
          {'xsi_type': 'ActivateCmsMetadataValues'}, statement.ToStatement())
      if result and int(result['numChanges']) > 0:
        values_activated += int(result['numChanges'])
      statement.offset += statement.limit
    else:
      break

  # Display results.
  if values_activated > 0:
    print('Number of CMS Metadata Values activated: %s' % values_activated)
  else:
    print('No CMS Metadata Values were activated.')


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, CMS_METADATA_KEY_ID)
