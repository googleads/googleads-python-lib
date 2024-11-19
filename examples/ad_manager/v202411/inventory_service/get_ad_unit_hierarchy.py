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

"""This example prints all ad unit names as a tree."""


# Import appropriate modules from the client library.
import collections
from googleads import ad_manager


def main(client):
  # Initialize appropriate services.
  network_service = client.GetService('NetworkService', version='v202411')
  inventory_service = client.GetService('InventoryService', version='v202411')

  # Set the parent ad unit's ID for all children ad units to be fetched from.
  current_network = network_service.getCurrentNetwork()
  root_ad_unit_id = current_network['effectiveRootAdUnitId']

  # Create a statement to select only the root ad unit by ID.
  statement = (ad_manager.StatementBuilder(version='v202411')
               .Where('id = :id')
               .OrderBy('id', ascending=True)
               .Limit(1)
               .WithBindVariable('id', root_ad_unit_id))

  # Make a request for the root ad unit
  response = inventory_service.getAdUnitsByStatement(statement.ToStatement())
  root_ad_unit = response['results'][0]

  all_ad_units = get_all_ad_units(inventory_service)

  display_hierarchy(root_ad_unit, all_ad_units)


def get_all_ad_units(inventory_service):
  """Download all ad units.

  Args:
    inventory_service: An instance of the InventoryService.

  Returns:
    A list containing all ad units.
  """
  # Create a statement to get all ad units.
  statement = (ad_manager.StatementBuilder(version='v202411')
               .OrderBy('id', ascending=True))

  # Pull down all ad units into a list
  keep_iterating = True
  total_results = 0
  found_ad_units = []
  while keep_iterating:
    page = inventory_service.getAdUnitsByStatement(statement.ToStatement())
    if 'results' in page and len(page['results']):
      total_results = page['totalResultSetSize']
      found_ad_units.extend(page['results'])

    statement.offset += statement.limit
    keep_iterating = statement.offset < total_results

  return found_ad_units


def display_hierarchy(root_ad_unit, all_ad_units):
  """Display the ad units as a tree.

  Args:
    root_ad_unit: The root ad unit to begin from.
    all_ad_units: A list containing all ad units.
  """
  # Create a dict mapping the ids of parents to lists of their children.
  parent_id_to_children = collections.defaultdict(list)
  for ad_unit in all_ad_units:
    if 'parentId' in ad_unit:
      parent_id_to_children[ad_unit['parentId']].append(ad_unit)
  parent_id_to_children = dict(parent_id_to_children)

  display_hierarchy_helper(root_ad_unit, parent_id_to_children, 0)


def display_hierarchy_helper(root, parent_id_to_children, depth):
  """Recursive helper for displaying the hierarchy.

  Args:
    root: The current root ad unit.
    parent_id_to_children: The overall map of parent ids to children.
    depth: The current depth.
  """
  print('%s%s (%s)' % ('%s+--' % ('|'.join(['  '] * depth)),
        root['name'], root['id']))

  # Recurse for each child of this root that has children.
  for child in parent_id_to_children.get(root['id'], []):
    display_hierarchy_helper(child, parent_id_to_children, depth + 1)


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
