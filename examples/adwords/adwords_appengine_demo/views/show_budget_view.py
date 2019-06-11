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

"""Handles request to view a Campaign's budget."""


import os

from handlers.api_handler import APIHandler
from handlers.ndb_handler import InitUser
import webapp2

from google.appengine.api import users
from google.appengine.ext.webapp import template


class ShowBudget(webapp2.RequestHandler):
  """View representing a Campaign's budget."""

  def get(self):
    """Handle get request."""
    client_customer_id = self.request.get('clientCustomerId')
    campaign_id = self.request.get('campaignId')
    budget_id = self.request.get('budgetId')

    template_values = {
        'back_url': '/showCampaigns?clientCustomerId=%s' % client_customer_id,
        'back_msg': 'View Campaigns.',
        'campaign_id': campaign_id,
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
                             app_user.adwords_manager_cid,
                             app_user.developer_token)

        budget = handler.GetBudget(client_customer_id, budget_id)
        # Use template to write output to the page.
        template_values['budget'] = budget
      except Exception as e:
        template_values['error'] = str(e)
    finally:
      path = os.path.join(os.path.dirname(__file__),
                          '../templates/show_budget.html')
      self.response.out.write(template.render(path, template_values))

  def post(self):
    """Handle post request."""
    client_customer_id = self.request.get('clientCustomerId')
    budget_id = self.request.get('budgetId')
    if not client_customer_id or not budget_id:
      self.redirect('/')
    else:
      self.redirect('/showBudget?clientCustomerId=%s&budgetId=%s'
                    % (client_customer_id, budget_id))
