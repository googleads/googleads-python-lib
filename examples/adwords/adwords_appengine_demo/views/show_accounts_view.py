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

"""Handles request to view accounts associated with manager account Id."""


import os

from handlers.api_handler import APIHandler
from handlers.ndb_handler import InitUser
import webapp2

from google.appengine.api import users
from google.appengine.ext.webapp import template


class ShowAccounts(webapp2.RequestHandler):
  """View showing the client accounts for a given manager account Id."""

  def get(self):
    """Handle get request."""
    template_values = {
        'back_url': '/showCredentials',
        'back_msg': 'View Credentials',
        'logout_url': users.create_logout_url('/'),
        'user_nickname': users.get_current_user().nickname()
    }
    try:
      try:
        app_user = InitUser()

        # Load Client instance.
        handler = APIHandler(app_user.client_id,
                             app_user.client_secret,
                             app_user.refresh_token,
                             app_user.adwords_manager_cid,
                             app_user.developer_token)

        # Fetch account info for each client account and place in template.
        template_values['accounts'] = handler.GetAccounts()
      except Exception as e:
        template_values['error'] = str(e)
    finally:
      # Use template to write output to the page.
      path = os.path.join(os.path.dirname(__file__),
                          '../templates/show_accounts.html')
      self.response.out.write(template.render(path, template_values))
