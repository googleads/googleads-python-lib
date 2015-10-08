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

"""Handles request to add a Campaign to a client account."""


import os

from handlers.api_handler import APIHandler
from handlers.ndb_handler import InitUser
import webapp2

from google.appengine.api import users
from google.appengine.ext.webapp import template


class AddCampaign(webapp2.RequestHandler):
  """View that either adds a Campaign or displays an error message."""

  def post(self):
    """Handle post request."""
    client_customer_id = self.request.get('clientCustomerId')
    campaign_name = self.request.get('campaignName')
    ad_channel_type = self.request.get('adChannelType')
    budget = self.request.get('budget')
    template_values = {
        'back_url': '/showCampaigns?clientCustomerId=%s' % client_customer_id,
        'back_msg': 'View Campaigns',
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

      # Create new campaign.
      handler.AddCampaign(client_customer_id, campaign_name,
                          ad_channel_type, budget)

      self.redirect('/showCampaigns?clientCustomerId=%s' % client_customer_id)
    except Exception, e:
      template_values['error'] = str(e)
      # Use template to write output to the page.
      path = os.path.join(os.path.dirname(__file__),
                          '../templates/base_template.html')
      self.response.out.write(template.render(path, template_values))
