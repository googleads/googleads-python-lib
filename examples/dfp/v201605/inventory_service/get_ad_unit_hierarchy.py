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

"""This code gets the ad unit hierarchy and displays it as a tree.

To create ad units, run create_ad_units.py

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  inventory_service = client.GetService('InventoryService', version='v201605')
  statement = dfp.FilterStatement()

  all_ad_units = []
  # Get ad units by statement.
  while True:
    response = inventory_service.getAdUnitsByStatement(
        statement.ToStatement())
    if 'results' in response:
      all_ad_units.extend(response['results'])
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  # Find the root ad unit. root_ad_unit can also be set to child unit to only
  # build and display a portion of the tree.
  query = 'WHERE parentId IS NULL'
  root_statement = dfp.FilterStatement(query)
  response = inventory_service.getAdUnitsByStatement(
      root_statement.ToStatement())
  root_ad_unit = response['results'][0]

  if root_ad_unit:
    BuildAndDisplayAdUnitTree(root_ad_unit, all_ad_units)
  else:
    print 'Could not build tree. No root ad unit found.'


def DisplayAdUnitTree(root_ad_unit, ad_unit_tree, depth=0):
  """Helper for displaying ad unit tree.

  Args:
    root_ad_unit: dict the root ad unit.
    ad_unit_tree: dict the tree of ad units.
    [optional]
    depth: int the depth the tree has reached.
  """
  print '%s%s (%s)' % (GenerateTab(depth), root_ad_unit['name'],
                       root_ad_unit['id'])
  if root_ad_unit['id'] in ad_unit_tree:
    for child in ad_unit_tree[root_ad_unit['id']]:
      DisplayAdUnitTree(child, ad_unit_tree, depth+1)


def GenerateTab(depth):
  """Generate tabs to represent branching to children.

  Args:
    depth: int the depth the tree has reached.

  Returns:
    string inserted in front of the root unit.
  """
  tab_list = []
  if depth > 0:
    tab_list.append('  ')
  tab_list.append('|  ' * depth)
  tab_list.append('+--')
  return ''.join(tab_list)


def BuildAndDisplayAdUnitTree(root_ad_unit, all_ad_units):
  """Create an ad unit tree and display it.

  Args:
    root_ad_unit: dict the root ad unit to build the tree under.
    all_ad_units: list the list of all ad units to build the tree with.
  """
  tree = {}
  for ad_unit in all_ad_units:
    if 'parentId' in ad_unit:
      if ad_unit['parentId'] not in tree:
        tree[ad_unit['parentId']] = []
      tree[ad_unit['parentId']].append(ad_unit)

  DisplayAdUnitTree(root_ad_unit, tree)

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
