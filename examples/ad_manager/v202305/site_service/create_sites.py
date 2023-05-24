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

"""This example creates a Site for Multiple Customer Management."""

# Import appropriate modules from the client library.
import sys
from googleads import ad_manager

# Set the URL and child network code for the Site.
URL = 'INSERT_URL_HERE'
CHILD_NETWORK_CODE = 'INSERT_CHILD_NETWORK_CODE_HERE'


def main(client, url, child_network_code):
  # Initialize appropriate services.
  network_service = client.GetService('NetworkService', version='v202305')
  site_service = client.GetService('SiteService', version='v202305')

  # Check that the child network code is approved for MANAGE_INVENTORY by this
  # network.
  current_network = network_service.getCurrentNetwork()
  child_network = None
  for child in current_network['childPublishers']:
    if child['childNetworkCode'] == child_network_code:
      child_network = child

  if child_network is None:
    print(('Child network %s not found on the current network (%s). Cannot '
           'create site.') % (child_network_code,
                              current_network['networkCode']))
    sys.exit(1)

  if child_network['approvedDelegationType'] != 'MANAGE_INVENTORY':
    print(('Child network %s has not approved for the current network (%s) '
           'to manage its inventory. Cannot create site.') % (
               child_network_code, current_network['networkCode']))
    sys.exit(1)

  # Create site object.
  site = {'url': url, 'childNetworkCode': child_network_code}

  # Create the site on the server.
  created_sites = site_service.createSites([site])

  # Display results.
  for site in created_sites:
    print('Site with id %d and URL "%s" was created for child network %s.' % (
        site['id'], site['url'], site['childNetworkCode']))


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, URL, CHILD_NETWORK_CODE)
