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


"""Adds a user list and populates it with hashed email addresses.

Note: It may take several hours for the list to be populated with members. Email
addresses must be associated with a Google account. For privacy purposes, the
user list size will show as zero until the list has at least 1000 members. After
that, the size will be rounded to the two most significant digits.
"""


import hashlib
import uuid

# Import appropriate modules from the client library.
from googleads import adwords


def main(client, emails):
  # Initialize appropriate services.
  user_list_service = client.GetService('AdwordsUserListService', 'v201601')

  user_list = {
      'xsi_type': 'CrmBasedUserList',
      'name': 'Customer relationship management list #%d' % uuid.uuid4(),
      'description': 'A list of customers that originated from email addresses',
      # Maximum lifespan is 180 days.
      'membershipLifeSpan': 180,
      # This field is optional. It links to a service you created that allows
      # members of this list to remove themselves.
      'optOutLink': 'http://endpoint1.example.com/optout'
  }

  # Create an operation to add the user list.
  operations = [{
      'operator': 'ADD',
      'operand': user_list
  }]

  result = user_list_service.mutate(operations)
  user_list_id = result['value'][0]['id']
  hashed_emails = HashEmails(emails)

  mutate_members_operation = {
      'operand': {
          'userListId': user_list_id,
          'dataType': 'EMAIL_SHA256',
          'members': hashed_emails
      },
      'operator': 'ADD'
  }

  response = user_list_service.mutateMembers([mutate_members_operation])

  if 'userLists' in response:
    for user_list in response['userLists']:
      print ('User list with name "%s" and ID "%d" was added.'
             % (user_list['name'], user_list['id']))


def HashEmails(emails):
  """Hashes the given emails using SHA-256.

  Note: Emails are stripped of any whitespace and set to lowercase before
  hashing.

  Args:
    emails: list of str emails to be hashed.

  Returns:
    A list of SHA-256 hashed emails.
  """
  return [hashlib.sha256(email.strip().lower()).hexdigest() for email in emails]


if __name__ == '__main__':
  EMAILS = ['customer1@example.com', 'customer2@example.com',
            ' Customer3@example.com ']

  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()
  main(adwords_client, EMAILS)
