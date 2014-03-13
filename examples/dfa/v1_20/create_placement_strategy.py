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

"""This example creates a placement strategy with the given name.

Tags: strategy.savePlacementStrategy
"""

__author__ = 'Joseph DiLallo'

import uuid

# Import appropriate classes from the client library.
from googleads import dfa


def main(client):
  # Initialize appropriate service.
  placement_strategy_service = client.GetService(
      'strategy', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Construct and save placement strategy.
  placement_strategy = {
      'name': 'Strategy %s' % uuid.uuid4()
  }
  result = placement_strategy_service.savePlacementStrategy(
      placement_strategy)

  # Display results.
  print 'Placement strategy with ID \'%s\' was created.' % result['id']


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client)
