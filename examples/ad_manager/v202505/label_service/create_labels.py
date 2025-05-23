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

"""This code example creates new labels.

To determine which labels exist, run get_all_labels.py.  This feature is only
available to Ad Manager 360 solution networks.
"""


import uuid

# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  # Initialize appropriate service.
  label_service = client.GetService('LabelService', version='v202505')

  # Create label objects.
  labels = []
  for _ in range(5):
    label = {
        'name': 'Label #%s' % uuid.uuid4(),
        'isActive': 'true',
        'types': ['COMPETITIVE_EXCLUSION']
    }
    labels.append(label)

  # Add Labels.
  labels = label_service.createLabels(labels)

  # Display results.
  for label in labels:
    print('Label with id "%s", name "%s", and types {%s} was found.'
          % (label['id'], label['name'], ','.join(label['types'])))

if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
