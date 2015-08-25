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

"""Handles request to view Campaigns associated with a given client account."""


import os

from handlers.api_handler import APIHandler
from handlers.ndb_handler import InitUser
import webapp2

from google.appengine.api import users
from google.appengine.ext.webapp import template


class ShowCampaigns(webapp2.RequestHandler):
  """View listing the Campaigns belonging to a client account."""

  def get(self):
    """Handle get request."""
    client_customer_id = self.request.get('clientCustomerId')

    template_values = {
        'back_url': '/showAccounts',
        'back_msg': 'View Accounts.',
        'ccid': client_customer_id,
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
                             app_user.mcc_cid,
                             app_user.developer_token)

        campaigns = handler.GetCampaigns(client_customer_id)
      except Exception, e:
        template_values['error'] = str(e)
    finally:
      # Use template to write output to the page.
      template_values['campaigns'] = campaigns
      path = os.path.join(os.path.dirname(__file__),
                          '../templates/show_campaigns.html')
      self.response.out.write(template.render(path, template_values))

  def post(self):
    """Handle post request."""
    client_customer_id = self.request.get('clientCustomerId')
    if not client_customer_id:
      self.redirect('/')
    else:
      self.redirect('/showCampaigns?clientCustomerId=%s' % client_customer_id)
