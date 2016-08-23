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

"""This code example creates a line item creative association for a creative
set.

To create creative sets, run create_creative_set.py. To create creatives, run
create_creatives.py. To determine which LICAs exist, run get_all_licas.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import dfp

CREATIVE_SET_ID = 'INSERT_CREATIVE_SET_ID_HERE'
LINE_ITEM_ID = 'INSERT_LINE_ITEM_ID_HERE'


def main(client, creative_set_id, line_item_id):
  # Initialize appropriate service.
  lica_service = client.GetService(
      'LineItemCreativeAssociationService', version='v201608')

  # Create LICA for a creative set.
  lica = {'creativeSetId': creative_set_id, 'lineItemId': line_item_id}

  # Add LICA.
  lica = lica_service.createLineItemCreativeAssociations([lica])

  # Display results.
  print (('LICA with line item ID \'%s\' and creative set ID \'%s\' was '
          'created.') % (lica['lineItemId'], lica['creativeSetId']))

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, CREATIVE_SET_ID, LINE_ITEM_ID)
