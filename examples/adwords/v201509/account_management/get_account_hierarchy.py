#!/usr/bin/python
#
# Copyright 2016 Google Inc. All Rights Reserved.
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

"""This example gets the account hierarchy under the current account.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

from googleads import adwords


PAGE_SIZE = 500


def DisplayAccountTree(account, accounts, links, depth=0):
  """Displays an account tree.

  Args:
    account: dict The account to display.
    accounts: dict Map from customerId to account.
    links: dict Map from customerId to child links.
    depth: int Depth of the current account in the tree.
  """
  prefix = '-' * depth * 2
  print '%s%s, %s' % (prefix, account['customerId'], account['name'])
  if account['customerId'] in links:
    for child_link in links[account['customerId']]:
      child_account = accounts[child_link['clientCustomerId']]
      DisplayAccountTree(child_account, accounts, links, depth + 1)


def main(client):
  # Initialize appropriate service.
  managed_customer_service = client.GetService(
      'ManagedCustomerService', version='v201509')

  # Construct selector to get all accounts.
  offset = 0
  selector = {
      'fields': ['CustomerId', 'Name'],
      'paging': {
          'startIndex': str(offset),
          'numberResults': str(PAGE_SIZE)
      }
  }
  more_pages = True
  accounts = {}
  child_links = {}
  parent_links = {}
  root_account = None

  while more_pages:
    # Get serviced account graph.
    page = managed_customer_service.get(selector)
    if 'entries' in page and page['entries']:
      # Create map from customerId to parent and child links.
      if 'links' in page:
        for link in page['links']:
          if link['managerCustomerId'] not in child_links:
            child_links[link['managerCustomerId']] = []
          child_links[link['managerCustomerId']].append(link)
          if link['clientCustomerId'] not in parent_links:
            parent_links[link['clientCustomerId']] = []
          parent_links[link['clientCustomerId']].append(link)
      # Map from customerID to account.
      for account in page['entries']:
        accounts[account['customerId']] = account
    offset += PAGE_SIZE
    selector['paging']['startIndex'] = str(offset)
    more_pages = offset < int(page['totalNumEntries'])

  # Find the root account.
  for customer_id in accounts:
    if customer_id not in parent_links:
      root_account = accounts[customer_id]

  # Display account tree.
  if root_account:
    print 'CustomerId, Name'
    DisplayAccountTree(root_account, accounts, child_links, 0)
  else:
    print 'Unable to determine a root account'


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()
  main(adwords_client)
