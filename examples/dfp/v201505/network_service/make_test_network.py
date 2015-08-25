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

"""This example creates a test network.

You do not need to have a DFP account to run this example, but you do need to
have a Google account (created at http://www.google.com/accounts/newaccount
if you currently don't have one) that is not associated with any other DFP test
networks. Once this network is created, you can supply the network code in your
settings to make calls to other services.

Alternatively, if you do not wish to run this example, you can create a test
network at:
https://dfp-playground.appspot.com
"""


# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  network_service = client.GetService('NetworkService', version='v201505')

  # Create a test network.
  network = network_service.MakeTestNetwork()

  # Display results.
  print ('Test network with network code \'%s\' and display name \'%s\' '
         'created.' % (network['networkCode'], network['displayName']))
  print ('You may now sign in at http://www.google.com/dfp/main?networkCode=%s'
         % network['networkCode'])

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
