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

"""This example creates a copy of an image creative.

To determine which image creatives exist, run get_image_creatives.py
"""

# Import appropriate modules from the client library.
from googleads import dfp

# Set the ID of the line item to pause.
PACKAGE_ID = 'INSERT_PACKAGE_ID_HERE'


def main(client):
  # Initialize appropriate service.
  package_service = client.GetService('PackageService', version='v201708')

  # Create a statement to select the single package.
  statement = (dfp.StatementBuilder()
               .Where('id = :id')
               .OrderBy('id', ascending=True)
               .Limit(1)
               .WithBindVariable('id', PACKAGE_ID))

  # Get the package.
  query_result = package_service.getPackagesByStatement(statement.ToStatement())

  package = query_result['results'][0]

  print ('Package with ID %d will create proposal line items using product '
         'package with ID %d.' % (package['id'],
                                  package['productPackageId']))

  # Remove limit and offset from statement.
  statement.limit = None
  statement.offset = None

  # Perform update packages action.
  result = package_service.performPackageAction(
      {'xsi_type': 'CreateProposalLineItemsFromPackages'},
      statement.ToStatement())

  if result and result['numChanges'] > 0:
    print ('Number of packages that proposal line items were created for: %d' %
           result['numChanges'])
  else:
    print 'No proposal line items were created.'


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
