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

"""Handler for ndb transactions."""


from models.app_user import AppUser

from google.appengine.api import users


def InitUser():
  """Initialize application user.

  Retrieve existing user credentials from datastore or add new user.

  Returns:
    AppUser instance of the application user.
  """
  result = AppUser.query(AppUser.user == users.get_current_user()).fetch()

  if result:
    app_user = result[0]
  else:
    app_user = AppUser(user=users.get_current_user(),
                       email=users.get_current_user().email())
    app_user.put()

  return app_user


def UpdateUserCredentials(client_id, client_secret, refresh_token, mcc_cid,
                          developer_token):
  """Update the credentials associated with application user.

  Args:
    client_id: str Client Id retrieved from the developer's console.
    client_secret: str Client Secret retrieved from the developer's console.
    refresh_token: str Refresh token generated with the above client id/secret.
    mcc_cid: str Customer Id for the AdWords MCC account.
    developer_token: str Developer Token for the AdWords account.
  """
  app_user = AppUser.query(AppUser.user == users.get_current_user()).fetch()[0]

  app_user.client_id = client_id
  app_user.client_secret = client_secret
  app_user.refresh_token = refresh_token
  app_user.mcc_cid = mcc_cid
  app_user.developer_token = developer_token

  app_user.put()
