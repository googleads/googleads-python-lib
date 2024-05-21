#!/usr/bin/env python
#
# Copyright 2017 Google Inc. All Rights Reserved.
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

"""Creates a native app install ad."""


import uuid

# Import appropriate modules from the client library.
from googleads import ad_manager


# This is the creative template ID for the system-defined native app install ad
# format, which we will create the native style from. Use
# CreativeTemplateService.getCreativeTemplateByStatement() and
# CreativeTemplate.isNativeEligible() to get other native ad formats available
# in your network.
CREATIVE_TEMPLATE_ID = 10004400
WIDTH = 300
HEIGHT = 345

HTML_SNIPPET = """<div id="adunit" style="overflow: hidden;">
  <img src="[%Thirdpartyimpressiontracker%]" style="display:none">
  <div class="attribution">Ad</div>
  <div class="image">
    <a class="image-link"
        href="%%CLICK_URL_UNESC%%[%Thirdpartyclicktracker%]%%DEST_URL%%"
        target="_top">
      <img src="[%Image%]">
    </a>
  </div>
  <div class="app-icon"><img src="[%Appicon%]"/></div>
  <div class="title">
    <a class="title-link"
        href="%%CLICK_URL_UNESC%%[%Thirdpartyclicktracker%]%%DEST_URL%%"
        target="_top">[%Headline%]</a>
  </div>
  <div class="reviews"></div>
  <div class="body">
    <a class="body-link"
        href="%%CLICK_URL_UNESC%%[%Thirdpartyclicktracker%]%%DEST_URL%%"
        target="_top">[%Body%]</a>
  </div>
  <div class="price">[%Price%]</div>
  <div class="button">
    <a class="button-link"
        href="%%CLICK_URL_UNESC%%[%Thirdpartyclicktracker%]%%DEST_URL%%"
        target="_top">[%Calltoaction%]</a>
  </div>
</div>
"""

CSS_SNIPPET = """body {
    background-color: rgba(255, 255, 255, 1);
    font-family: "Roboto-Regular", sans-serif;
    font-weight: normal;
    font-size: 12px;
    line-height: 14px;
}
.attribution {
    background-color: rgba(236, 182, 0, 1);
    color: rgba(255, 255, 255, 1);
    font-size: 13px;
    display: table;
    margin: 4px 8px;
    padding: 0 3px;
    border-radius: 2px;
}
.image {
    text-align: center;
    margin: 8px;
}
.image img,
.image-link {
    width: 100%;
}
.app-icon {
    float: left;
    margin: 0 8px 4px 8px;
    height: 40px;
    width: 40px;
    background-color: transparent;
}
.app-icon img {
    height: 100%;
    width: 100%;
    border-radius: 20%;
}
.title {
    font-weight: bold;
    font-size: 14px;
    line-height: 20px;
    margin: 8px 8px 4px 8px;
}
.title a {
    color: rgba(112, 112, 112, 1);
    text-decoration: none;
}
.reviews {
    float: left;
}
.reviews svg {
    fill: rgba(0, 0, 0, 0.7);
}
.body {
    clear: left;
    margin: 8px;
}
.body a {
    color: rgba(110, 110, 110, 1);
    text-decoration: none;
}
.price {
    display: none;
}
.button {
    font-size: 14px;
    font-weight: bold;
    float: right;
    margin: 0px 16px 16px 0px;
    white-space: nowrap;
}
.button a {
    color: #2196F3;
    text-decoration: none;
}
.button svg {
    display: none;
}
"""


def main(client, html_snippet, css_snippet, creative_template_id, width,
         height):
  # Initialize appropriate service.
  native_style_service = client.GetService('NativeStyleService',
                                           version='v202405')

  native_style = {
      'name': 'Native style #%d' % uuid.uuid4(),
      'htmlSnippet': html_snippet,
      'cssSnippet': css_snippet,
      'creativeTemplateId': creative_template_id,
      'size': {
          'width': width,
          'height': height,
          'isAspectRatio': False
      }
  }

  # Create the native style on the server.
  native_styles = native_style_service.createNativeStyles([native_style])

  # Display results.
  for native_style in native_styles:
    print('A Native style with ID "%s", name "%s", and creative template ID'
          '"%d" was created.' % (native_style['id'], native_style['name'],
                                 native_style['creativeTemplateId']))


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, HTML_SNIPPET, CSS_SNIPPET, CREATIVE_TEMPLATE_ID,
       WIDTH, HEIGHT)
