#!/usr/bin/python
#
# Copyright 2013 Google Inc. All Rights Reserved.
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

"""Unit tests to cover the oauth2 module."""

__author__ = 'Joseph DiLallo'

import io
import sys
import unittest
import urllib2

import mock
from oauthlib import oauth2

import googleads.oauth2
from googleads import errors

PYTHON2 = sys.version_info[0] == 2
URL_REQUEST_PATH = ('urllib2' if PYTHON2 else 'urllib.request')


class GoogleOAuth2ClientTest(unittest.TestCase):
  """Tests for the googleads.oauth2.GoogleOAuth2Client class."""

  def testCreateHttpHeader(self):
    """For coverage."""
    self.assertRaises(
        NotImplementedError,
        googleads.oauth2.GoogleOAuth2Client().CreateHttpHeader)


class GoogleRefreshTokenClientTest(unittest.TestCase):
  """Tests for the googleads.oauth2.GoogleRefreshTokenClient class."""

  def setUp(self):
    self.client_id = 'client_id'
    self.client_secret = 'itsasecret'
    self.refresh_token = 'refreshing'
    self.https_proxy = 'my.proxy.com:443'
    with mock.patch('oauthlib.oauth2.BackendApplicationClient'
                   ) as mock_oauthlib_client:
      self.oauthlib_client = mock_oauthlib_client.return_value
      self.googleads_client = googleads.oauth2.GoogleRefreshTokenClient(
          self.client_id, self.client_secret, self.refresh_token,
          self.https_proxy)

  def testCreateHttpHeader_noRefresh(self):
    header = {'Authorization': 'b'}
    self.oauthlib_client.add_token.return_value = ('unused', header, 'unusued')
    self.assertEqual(header, self.googleads_client.CreateHttpHeader())

  def testCreateHttpHeader_refresh(self):
    header = {u'Authorization': 'b'}
    post_body = 'post_body'
    content = u'content'
    fake_request = io.StringIO() if PYTHON2 else io.BytesIO()
    fake_request.write(content if PYTHON2 else bytes(content, 'utf-8'))
    fake_request.seek(0)
    self.oauthlib_client.add_token.side_effect = [oauth2.TokenExpiredError(),
                                                  ('unused', header, 'unusued')]
    self.oauthlib_client.prepare_refresh_body.return_value = post_body

    with mock.patch(URL_REQUEST_PATH + '.build_opener') as mock_opener:
      with mock.patch(URL_REQUEST_PATH + '.Request') as mock_request:
        mock_opener.return_value.open.return_value = fake_request
        returned_header = self.googleads_client.CreateHttpHeader()

        mock_request.assert_called_once_with(
            mock.ANY, post_body if PYTHON2 else bytes(post_body, 'utf-8'),
            mock.ANY)
        mock_opener.return_value.open.assert_called_once_with(
            mock_request.return_value)
    self.assertEqual(header, returned_header)
    self.oauthlib_client.parse_request_body_response.assert_called_once_with(
        content)
    self.assertEqual(2, len(self.oauthlib_client.add_token.call_args_list))
    self.assertEqual(str, type(returned_header.keys()[0]))

  def testCreateHttpHeader_refreshFails(self):
    request_body = 'request_body'
    response_body = u'{ "error": "invalid_grant" }'
    error = urllib2.HTTPError('', 400, 'Bad Request', {},
                              io.StringIO(response_body))

    self.oauthlib_client.add_token.side_effect = oauth2.TokenExpiredError()
    self.oauthlib_client.prepare_refresh_body.return_value = request_body

    with mock.patch(URL_REQUEST_PATH + '.build_opener') as mock_opener:
      with mock.patch(URL_REQUEST_PATH + '.Request') as mock_request:
        mock_opener.return_value.open.side_effect = error
        self.assertRaises(errors.OAuthInvalidGrantError,
            self.googleads_client.CreateHttpHeader)

        mock_request.assert_called_once_with(
            mock.ANY, request_body if PYTHON2 else bytes(post_body, 'utf-8'),
            mock.ANY)
        mock_opener.return_value.open.assert_called_once_with(
            mock_request.return_value)
    self.assertFalse(self.oauthlib_client.parse_request_body_response.called)
    self.oauthlib_client.add_token.assert_called_once_with(mock.ANY)


if __name__ == '__main__':
  unittest.main()
