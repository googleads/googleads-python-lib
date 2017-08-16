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

"""This code example creates a new creative wrapper.

Creative wrappers must be associated with a LabelType.CREATIVE_WRAPPER label and
applied to ad units by AdUnit.appliedLabels. To determine which creative
wrappers exist, run get_all_creative_wrappers.py

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import dfp

LABEL_ID = 'INSERT_CREATIVE_WRAPPER_LABEL_ID_HERE'


def main(client, label_id):
  # Initialize appropriate service.
  creative_wrapper_service = client.GetService('CreativeWrapperService',
                                               version='v201708')

  # Create creative wrapper objects.
  creative_wrapper = {
      # A label can only be associated with one creative wrapper.
      'labelId': label_id,
      'ordering': 'INNER',
      'htmlHeader': '<b>My creative wrapper header</b>',
      'htmlFooter': '<b>My creative wrapper footer</b>'
  }

  # Add creative wrapper.
  creative_wrappers = creative_wrapper_service.createCreativeWrappers(
      [creative_wrapper])

  # Display results.
  for creative_wrapper in creative_wrappers:
    print ('Creative wrapper with ID "%s" applying to label "%s" was '
           'created.' % (creative_wrapper['id'], creative_wrapper['labelId']))

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, LABEL_ID)
