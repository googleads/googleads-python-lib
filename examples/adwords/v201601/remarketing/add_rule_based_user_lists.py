#!/usr/bin/python
#
# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This example adds two rule-based remarketing user lists.

Adds two rule-based remarketing user lists; one with no site visit date
restrictions and another that will only include users who visit your site in
the next six months.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


import calendar
from datetime import date
from datetime import datetime
from datetime import timedelta

from googleads import adwords


def main(client):
  # Initialize appropriate service.
  adwords_user_list_service = client.GetService(
      'AdwordsUserListService', version='v201601')

  # First rule item group - users who visited the checkout page and had more
  # than one item in their shopping cart.
  checkout_rule_item = {
      'StringRuleItem': {
          'key': {
              'name': 'ecomm_pagetype'
          },
          'op': 'EQUALS',
          'value': 'checkout'
      }
  }

  cart_size_rule_item = {
      'NumberRuleItem': {
          'key': {
              'name': 'cartsize'
          },
          'op': 'GREATER_THAN',
          'value': '1.0'
      }
  }

  # Combine the two rule items into a RuleItemGroup so AdWords will logically
  # AND the rules together.
  checkout_multiple_item_group = {
      'items': [checkout_rule_item, cart_size_rule_item]
  }

  # Second rule item group - users who checked out within the next 3 months.
  today = date.today()
  start_date_rule_item = {
      'DateRuleItem': {
          'key': {
              'name': 'checkoutdate'
          },
          'op': 'AFTER',
          'value': today.strftime('%Y%m%d')
      }
  }

  three_months_later = AddMonths(today, 3)

  three_months_later_rule_item = {
      'DateRuleItem': {
          'key': {
              'name': 'checkoutdate'
          },
          'op': 'BEFORE',
          'value': three_months_later.strftime('%Y%m%d')
      }
  }

  # Combine the date rule items into a RuleItemGroup
  checked_out_date_range_item_group = {
      'items': [start_date_rule_item, three_months_later_rule_item]
  }

  # Combine the rule item groups into a Rule so AdWords will logically OR the
  # groups together.
  rule = {
      'groups': [
          checkout_multiple_item_group,
          checked_out_date_range_item_group
      ]
  }

  # Create the user list with no restrictions on site visit date.
  expression_user_list = {
      'xsi_type': 'ExpressionRuleUserList',
      'name': 'Expression-based user list created at %s'
              % datetime.today().strftime('%Y%m%d %H:%M:%S'),
      'description': 'Users who checked out in three month window OR visited'
                     ' the checkout page with more than one item in their'
                     ' cart.',
      'rule': rule
  }

  # Create the user list restricted to users who visit your site within the next
  # six months.
  end_date = AddMonths(today, 6)

  date_user_list = {
      'xsi_type': 'DateSpecificRuleUserList',
      'name': 'Date rule user list created at %s'
              % datetime.today().strftime('%Y%m%d %H:%M:%S'),
      'description': 'Users who visited the site between %s and %s and checked'
                     ' out in three month window OR visited the checkout page'
                     ' with more than one item in their cart.'
                     % (today.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')),
      'rule': rule,
      'startDate': today.strftime('%Y%m%d'),
      'endDate': end_date.strftime('%Y%m%d')
  }

  # Create operations to add the user lists.
  operations = [
      {
          'operand': user_list,
          'operator': 'ADD',
      } for user_list in [expression_user_list, date_user_list]
  ]

  # Submit the operations.
  user_lists = adwords_user_list_service.mutate(operations)

  # Display results.
  for user_list in user_lists['value']:
    print (('User list added with ID %d, name "%s", status "%s", list type'
            ' "%s", accountUserListStatus "%s", description "%s".') %
           (user_list['id'], user_list['name'],
            user_list['status'], user_list['listType'],
            user_list['accountUserListStatus'], user_list['description']))


def AddMonths(start_date, months):
  """A simple convenience utility for adding months to a given start date.

  This increments the months by adding the number of days in the current month
  to the current month, for each month.

  Args:
    start_date: date The date months are being added to.
    months: int The number of months to add.

  Returns:
    A date equal to the start date incremented by the given number of months.
  """
  current_date = start_date
  i = 0
  while i < months:
    month_days = calendar.monthrange(current_date.year, current_date.month)[1]
    current_date += timedelta(days=month_days)
    i += 1
  return current_date


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client)
