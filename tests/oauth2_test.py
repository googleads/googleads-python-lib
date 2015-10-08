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


import datetime
import unittest


import httplib2
import mock
import socks

import googleads.errors
import googleads.oauth2

import fake_filesystem
import fake_tempfile
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2Credentials
from oauth2client.client import SignedJwtAssertionCredentials


class GetAPIScopeTest(unittest.TestCase):
  """Tests for the googleads.oauth2.GetAPIScope function."""

  def setUp(self):
    self.api_name_adwords = 'adwords'
    self.api_name_dfa = 'dfa'
    self.api_name_dfp = 'dfp'
    self.scope_adwords = 'https://www.googleapis.com/auth/adwords'
    self.scope_dfa = 'https://www.googleapis.com/auth/dfatrafficking'
    self.scope_dfp = 'https://www.googleapis.com/auth/dfp'

  def testGetAPIScope_adwords(self):
    self.assertEquals(googleads.oauth2.GetAPIScope(self.api_name_adwords),
                      self.scope_adwords)

  def testGetAPIScope_badKey(self):
    self.assertRaises(googleads.errors.GoogleAdsValueError,
                      googleads.oauth2.GetAPIScope, 'fake_api_name')

  def testGetAPIScope_dfa(self):
    self.assertEquals(googleads.oauth2.GetAPIScope(self.api_name_dfa),
                      self.scope_dfa)

  def testGetAPIScope_dfp(self):
    self.assertEquals(googleads.oauth2.GetAPIScope(self.api_name_dfp),
                      self.scope_dfp)


class GoogleOAuth2ClientTest(unittest.TestCase):
  """Tests for the googleads.oauth2.GoogleOAuth2Client class."""

  def testCreateHttpHeader(self):
    """For coverage."""
    self.assertRaises(
        NotImplementedError,
        googleads.oauth2.GoogleOAuth2Client().CreateHttpHeader)

  def testRefresh(self):
    """For coverage."""
    self.assertRaises(
        NotImplementedError,
        googleads.oauth2.GoogleOAuth2Client().Refresh)


class GoogleRefreshTokenClientTest(unittest.TestCase):
  """Tests for the googleads.oauth2.GoogleRefreshTokenClient class."""

  def setUp(self):
    self.client_id = 'client_id'
    self.client_secret = 'itsasecret'
    self.refresh_token = 'refreshing'
    self.proxy_info = httplib2.ProxyInfo(socks.PROXY_TYPE_HTTP, 'myproxy.com',
                                         443)
    self.https_proxy = '%s:%s' % (self.proxy_info.proxy_host,
                                  self.proxy_info.proxy_port)
    self.access_token_unrefreshed = 'a'
    self.access_token_refreshed = 'b'

    # Mock out httplib2.Http for testing.
    self.http = mock.Mock(spec=httplib2.Http)
    self.opener = self.http.return_value = mock.Mock()
    self.opener.proxy_info = self.proxy_info
    self.opener.ca_certs = None
    self.opener.disable_ssl_certificate_valiation = True

    # Mock out oauth2client.client.OAuth2Credentials for testing
    self.oauth2_credentials = mock.Mock(spec=OAuth2Credentials)
    self.mock_oauth2_credentials = self.oauth2_credentials.return_value = (
        mock.Mock())
    self.mock_oauth2_credentials.access_token = self.access_token_unrefreshed
    self.mock_oauth2_credentials.token_expiry = datetime.datetime(1980, 1, 1,
                                                                  12)

    def apply(headers):
      headers['Authorization'] = ('Bearer %s'
                                  % self.mock_oauth2_credentials.access_token)

    def refresh(mock_http):
      self.mock_oauth2_credentials.access_token = self.access_token_refreshed
      self.mock_oauth2_credentials.token_expiry = datetime.datetime.utcnow()

    self.mock_oauth2_credentials.apply = mock.Mock(side_effect=apply)
    self.mock_oauth2_credentials.refresh = mock.Mock(side_effect=refresh)
    with mock.patch('oauth2client.client.OAuth2Credentials',
                    self.oauth2_credentials):
      self.googleads_client = googleads.oauth2.GoogleRefreshTokenClient(
          self.client_id, self.client_secret, self.refresh_token,
          self.proxy_info)

  def testCreateHttpHeader_noRefresh(self):
    header = {'Authorization': 'Bearer %s' % self.access_token_unrefreshed}
    self.mock_oauth2_credentials.token_expiry = None
    self.assertEqual(header, self.googleads_client.CreateHttpHeader())

  def testCreateHttpHeader_refresh(self):
    header = {u'Authorization': 'Bearer %s' % self.access_token_refreshed}

    with mock.patch('httplib2.Http', self.http):
      self.assertEqual(header, self.googleads_client.CreateHttpHeader())
      self.http.assert_called_once_with(
          ca_certs=None, proxy_info=self.proxy_info,
          disable_ssl_certificate_validation=False)
      self.mock_oauth2_credentials.refresh.assert_called_once_with(
          self.opener)

  def testCreateHttpHeader_refreshFails(self):
    self.mock_oauth2_credentials.refresh.side_effect = AccessTokenRefreshError(
        'Invalid response 400')

    with mock.patch('httplib2.Http', self.http):
      self.assertRaises(AccessTokenRefreshError,
                        self.googleads_client.CreateHttpHeader)
      self.assertFalse(self.mock_oauth2_credentials.apply.called)


class GoogleServiceAccountTest(unittest.TestCase):
  """Tests for the googleads.oauth2.GoogleServiceAccountClient class."""

  def setUp(self):
    self.scope = 'scope'
    self.service_account_email = 'email@email.com'
    self.private_key_password = 'notasecret'
    self.proxy_info = httplib2.ProxyInfo(socks.PROXY_TYPE_HTTP, 'myproxy.com',
                                         443)
    self.https_proxy = '%s:%s' % (self.proxy_info.proxy_host,
                                  self.proxy_info.proxy_port)
    self.access_token_unrefreshed = 'a'
    self.access_token_refreshed = 'b'

    # Mock out filesystem and file for testing.
    filesystem = fake_filesystem.FakeFilesystem()
    tempfile = fake_tempfile.FakeTempfileModule(filesystem)
    fake_open = fake_filesystem.FakeFileOpen(filesystem)
    key_file_path = tempfile.NamedTemporaryFile(delete=False).name

    with fake_open(key_file_path, 'w') as file_handle:
      file_handle.write('IT\'S A SECRET TO EVERYBODY.')

    # Mock out httplib2.Http for testing.
    self.http = mock.Mock(spec=httplib2.Http)
    self.opener = self.http.return_value = mock.Mock()
    self.opener.proxy_info = self.proxy_info
    self.opener.ca_certs = None
    self.opener.disable_ssl_certificate_valiation = True

    # Mock out oauth2client.client.OAuth2Credentials for testing
    self.oauth2_credentials = mock.Mock(spec=SignedJwtAssertionCredentials)
    self.mock_oauth2_credentials = self.oauth2_credentials.return_value = (
        mock.Mock())
    self.mock_oauth2_credentials.access_token = 'x'
    self.mock_oauth2_credentials.token_expiry = datetime.datetime(1980, 1, 1,
                                                                  12)

    def apply(headers):
      headers['Authorization'] = ('Bearer %s'
                                  % self.mock_oauth2_credentials.access_token)

    def refresh(mock_http):
      self.mock_oauth2_credentials.access_token = (
          self.access_token_unrefreshed if
          self.mock_oauth2_credentials.access_token is 'x'
          else self.access_token_refreshed)
      self.mock_oauth2_credentials.token_expiry = datetime.datetime.utcnow()

    self.mock_oauth2_credentials.apply = mock.Mock(side_effect=apply)
    self.mock_oauth2_credentials.refresh = mock.Mock(side_effect=refresh)
    with mock.patch('__builtin__.open', fake_open):
      with mock.patch('oauth2client.client.SignedJwtAssertionCredentials',
                      self.oauth2_credentials):
        self.googleads_client = googleads.oauth2.GoogleServiceAccountClient(
            self.scope, self.service_account_email, key_file_path,
            self.private_key_password, proxy_info=self.proxy_info)
      # Undo the call count for the auto-refresh
      self.mock_oauth2_credentials.refresh.reset_mock()

  def testCreateHttpHeader_noRefresh(self):
    header = {'Authorization': 'Bearer %s' % self.access_token_unrefreshed}
    self.mock_oauth2_credentials.token_expiry = None
    self.assertEqual(header, self.googleads_client.CreateHttpHeader())

  def testCreateHttpHeader_refresh(self):
    header = {u'Authorization': 'Bearer %s' % self.access_token_refreshed}

    with mock.patch('httplib2.Http', self.http):
      self.assertEqual(header, self.googleads_client.CreateHttpHeader())
      self.http.assert_called_once_with(
          ca_certs=None, proxy_info=self.proxy_info,
          disable_ssl_certificate_validation=False)
      self.mock_oauth2_credentials.refresh.assert_called_once_with(
          self.opener)

  def testCreateHttpHeader_refreshFails(self):
    self.mock_oauth2_credentials.refresh.side_effect = AccessTokenRefreshError(
        'Invalid response 400')

    with mock.patch('httplib2.Http', self.http):
      self.assertRaises(AccessTokenRefreshError,
                        self.googleads_client.CreateHttpHeader)
      self.assertFalse(self.mock_oauth2_credentials.apply.called)


if __name__ == '__main__':
  unittest.main()
