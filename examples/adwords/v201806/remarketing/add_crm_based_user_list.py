#!/usr/bin/env python
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


def main(client):
  # Initialize appropriate services.
  user_list_service = client.GetService('AdwordsUserListService', 'v201806')

  user_list = {
      'xsi_type': 'CrmBasedUserList',
      'name': 'Customer relationship management list #%d' % uuid.uuid4(),
      'description': 'A list of customers that originated from email addresses',
      # CRM-based user lists can use a membershipLifeSpan of 10000 to indicate
      # unlimited; otherwise normal values apply.
      'membershipLifeSpan': 30,
      'uploadKeyType': 'CONTACT_INFO'
  }

  # Create an operation to add the user list.
  operations = [{
      'operator': 'ADD',
      'operand': user_list
  }]

  result = user_list_service.mutate(operations)
  user_list_id = result['value'][0]['id']

  emails = ['customer1@example.com', 'customer2@example.com',
            ' Customer3@example.com ']
  members = [{'hashedEmail': NormalizeAndSHA256(email)} for email in emails]

  # Add address info.
  members.append({
      'addressInfo': {
          # First and last name must be normalized and hashed.
          'hashedFirstName': NormalizeAndSHA256('John'),
          'hashedLastName': NormalizeAndSHA256('Doe'),
          # Country code and zip code are sent in plaintext.
          'countryCode': 'US',
          'zipCode': '10001'
      }
  })

  mutate_members_operation = {
      'operand': {
          'userListId': user_list_id,
          'membersList': members
      },
      'operator': 'ADD'
  }

  response = user_list_service.mutateMembers([mutate_members_operation])

  if 'userLists' in response:
    for user_list in response['userLists']:
      print ('User list with name "%s" and ID "%d" was added.'
             % (user_list['name'], user_list['id']))


def NormalizeAndSHA256(s):
  """Normalizes (lowercase, remove whitespace) and hashes a string with SHA-256.

  Args:
    s: The string to perform this operation on.

  Returns:
    A normalized and SHA-256 hashed string.
  """
  return hashlib.sha256(s.strip().lower()).hexdigest()


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()
  main(adwords_client)
