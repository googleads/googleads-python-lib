#!/usr/bin/env python
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

"""Model representing a user of the application."""


from google.appengine.ext import ndb


class AppUser(ndb.Model):
  """Implements AppUser.

  The AppUser represents an API user in a datastore. For each user, we store
  their email address and API credentials.
  """
  user = ndb.UserProperty(required=True)
  date = ndb.DateProperty(auto_now=True)
  email = ndb.StringProperty(required=True)
  client_id = ndb.StringProperty(required=False)
  client_secret = ndb.StringProperty(required=False)
  refresh_token = ndb.StringProperty(required=False)
  adwords_manager_cid = ndb.StringProperty(required=False)
  developer_token = ndb.StringProperty(required=False)
