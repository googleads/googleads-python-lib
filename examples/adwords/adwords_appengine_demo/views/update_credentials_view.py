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

"""Handles requests to update the current user's credentials."""


import os

from handlers.ndb_handler import UpdateUserCredentials
import webapp2

from google.appengine.api import users
from google.appengine.ext.webapp import template


class UpdateCredentials(webapp2.RequestHandler):
  """View that updates the user's credentials or displays an error message."""

  def post(self):
    """Handle post request."""
    template_values = {
        'back_url': '/showCredentials',
        'back_msg': 'View Credentials',
        'logout_url': users.create_logout_url('/'),
        'user_nickname': users.get_current_user().nickname()
    }
    try:
      UpdateUserCredentials(self.request.get('client_id'),
                            self.request.get('client_secret'),
                            self.request.get('refresh_token'),
                            self.request.get('manager_account_id'),
                            self.request.get('dev_token'))
      self.redirect('/showCredentials')
    except Exception, e:
      template_values['error'] = str(e)
      # Use template to write output to the page.
      path = os.path.join(os.path.dirname(__file__),
                          '../templates/base_template.html')
      self.response.out.write(template.render(path, template_values))
