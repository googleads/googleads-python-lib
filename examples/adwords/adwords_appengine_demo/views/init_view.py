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

"""View at the root directory of the application."""


import logging

from handlers.ndb_handler import InitUser
import webapp2


class InitView(webapp2.RequestHandler):
  """View that checks whether credentials are stored for user and redirects."""

  def get(self):
    """Handle get request."""
    try:
      app_user = InitUser()

      if (app_user.client_id and app_user.client_secret and
          app_user.adwords_manager_cid and app_user.developer_token and
          app_user.refresh_token):
        self.redirect('/showAccounts')
      else:
        self.redirect('/showCredentials')
    except Exception as e:
      logging.debug(str(e))
