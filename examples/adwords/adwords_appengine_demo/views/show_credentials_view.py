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
"""Handles requests to view the user's credentials."""


import os

from handlers.ndb_handler import InitUser
import webapp2

from google.appengine.api import users
from google.appengine.ext.webapp import template


class ShowCredentials(webapp2.RequestHandler):
  """View showing the credentials of the current user."""

  def get(self):
    """Handle get request."""
    template_values = {
        'back_url': '/',
        'back_msg': 'View Accounts',
        'logout_url': users.create_logout_url('/'),
        'user_nickname': users.get_current_user().nickname()
    }
    try:
      try:
        app_user = InitUser()

        template_values['email'] = app_user.email if app_user.email else ''
        template_values['client_id'] = (app_user.client_id if app_user.client_id
                                        else '')
        template_values['client_secret'] = (app_user.client_secret if
                                            app_user.client_secret else '')
        template_values['refresh_token'] = (app_user.refresh_token if
                                            app_user.refresh_token else '')
        template_values['adwords_manager_cid'] = (
            app_user.adwords_manager_cid if app_user.adwords_manager_cid else ''
        )
        template_values['dev_token'] = (app_user.developer_token if
                                        app_user.developer_token else '')
      except Exception, e:
        template_values['error'] = str(e)
    finally:
      # Use template to write output to the page.
      path = os.path.join(os.path.dirname(__file__),
                          '../templates/show_credentials.html')
      self.response.out.write(template.render(path, template_values))
