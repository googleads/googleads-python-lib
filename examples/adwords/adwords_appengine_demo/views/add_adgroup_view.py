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

"""Handles request to add an AdGroup to a Campaign."""


import os

from handlers.api_handler import APIHandler
from handlers.ndb_handler import InitUser
import webapp2

from google.appengine.api import users
from google.appengine.ext.webapp import template


class AddAdGroup(webapp2.RequestHandler):
  """View that either adds an AdGroup or displays an error message."""

  def post(self):
    """Handle post request."""
    client_customer_id = self.request.get('clientCustomerId')
    campaign_id = self.request.get('campaignId')
    campaign_name = self.request.get('name')
    campaign_status = self.request.get('status')
    template_values = {
        'back_url': ('/showAdGroups?clientCustomerId=%s&campaignId=%s' %
                     (client_customer_id, campaign_id)),
        'back_msg': 'View AdGroups',
        'logout_url': users.create_logout_url('/'),
        'user_nickname': users.get_current_user().nickname()
    }
    try:
      app_user = InitUser()
      # Load Client instance.
      handler = APIHandler(app_user.client_id,
                           app_user.client_secret,
                           app_user.refresh_token,
                           app_user.adwords_manager_cid,
                           app_user.developer_token)

      # Create new ad group.
      handler.AddAdGroup(client_customer_id, campaign_id, campaign_name,
                         campaign_status)

      self.redirect('/showAdGroups?clientCustomerId=%s&campaignId=%s'
                    % (client_customer_id, campaign_id))
    except Exception as e:
      template_values['error'] = str(e)
      # Use template to write output to the page.
      path = os.path.join(os.path.dirname(__file__),
                          '../templates/base_template.html')
      self.response.out.write(template.render(path, template_values))
