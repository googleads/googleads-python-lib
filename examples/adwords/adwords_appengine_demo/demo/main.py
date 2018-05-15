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
"""App Engine application module.

Configures the web application that will display the AdWords UI.
"""


from demo import DEBUG
from requests_toolbelt.adapters import appengine
from views import AddAdGroup
from views import AddCampaign
from views import InitView
from views import ShowAccounts
from views import ShowAdGroups
from views import ShowBudget
from views import ShowCampaigns
from views import ShowCredentials
from views import UpdateBudget
from views import UpdateCredentials
import webapp2

# Patch requests library for use on App Engine.
appengine.monkeypatch()

app = webapp2.WSGIApplication([('/', InitView),
                               ('/showCredentials', ShowCredentials),
                               ('/updateCredentials', UpdateCredentials),
                               ('/showAccounts', ShowAccounts),
                               ('/showCampaigns', ShowCampaigns),
                               ('/addCampaign', AddCampaign),
                               ('/showAdGroups', ShowAdGroups),
                               ('/addAdGroup', AddAdGroup),
                               ('/showBudget', ShowBudget),
                               ('/updateBudget', UpdateBudget)],
                              debug=DEBUG)
