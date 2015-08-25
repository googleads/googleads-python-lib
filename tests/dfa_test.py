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

"""Unit tests to cover the dfa module."""


import unittest

import mock
import suds.transport

import googleads.dfa
import googleads.common
import googleads.errors


class DfaHeaderHandlerTest(unittest.TestCase):
  """Tests for the googleads.dfa._DfaHeaderHandler class."""

  def setUp(self):
    self.dfa_client = mock.Mock()
    self.header_handler = googleads.dfa._DfaHeaderHandler(self.dfa_client)

  def testSetHeaders(self):
    suds_client = mock.Mock()
    request_header_element = mock.Mock()
    app_name_element = mock.Mock()
    app_name_element.setText.return_value = app_name_element
    username = 'my username is name'
    app_name = 'application name'
    oauth_header = {'oauth', 'header'}
    self.dfa_client.username = username
    self.dfa_client.application_name = app_name
    self.dfa_client.oauth2_client.CreateHttpHeader.return_value = (
        oauth_header)
    element_mocks = {'RequestHeader': request_header_element,
                     'applicationName': app_name_element}

    with mock.patch('suds.wsse') as mock_wsse:
      with mock.patch('suds.sax') as mock_sax:
        mock_sax.element.Element.side_effect = lambda x: element_mocks[x]

        self.header_handler.SetHeaders(suds_client)

        mock_wsse.Security.assert_called_once_with()
        mock_wsse.UsernameToken.assert_called_once_with(username)
        mock_wsse.Security.return_value.tokens.append.assert_called_once_with(
            mock_wsse.UsernameToken.return_value)

        app_name_element.setText.assert_called_once_with(
            ''.join([app_name, googleads.dfa._DfaHeaderHandler._LIB_SIG]))
        request_header_element.append.assert_called_once_with(app_name_element)

        suds_client.set_options.assert_any_call(
            wsse=mock_wsse.Security.return_value,
            soapheaders=request_header_element,
            headers=oauth_header)


class DfaClientTest(unittest.TestCase):
  """Tests for the googleads.dfa.DfaClient class."""

  def setUp(self):
    self.username = 'dfa_user_1'
    self.application_name = 'application name'
    self.oauth2_client = 'unused'
    self.https_proxy = 'myproxy.com:443'
    self.cache = None
    self.dfa_client = googleads.dfa.DfaClient(
        self.username, self.oauth2_client, self.application_name,
        self.https_proxy, self.cache)

  def testLoadFromStorage(self):
    with mock.patch('googleads.common.LoadFromStorage') as mock_load:
      mock_load.return_value = {
          'username': 'abcdEFghIjkLMOpqRs',
          'oauth2_client': True,
          'application_name': 'unit testing'
      }
      self.assertIsInstance(googleads.dfa.DfaClient.LoadFromStorage(),
                            googleads.dfa.DfaClient)

  def testGetService_success(self):
    version = googleads.dfa.DfaClient._SERVICE_MAP.keys()[0]
    service = googleads.dfa.DfaClient._SERVICE_MAP[version][0]

    # Use a custom server. Also test what happens if the server ends with a
    # trailing slash
    server = 'https://testing.test.com/'
    https_proxy = {'https': self.https_proxy}
    with mock.patch('suds.client.Client') as mock_client:
      suds_service = self.dfa_client.GetService(service, version, server)

      mock_client.assert_called_once_with(
          'https://testing.test.com/%s/api/dfa-api/%s?wsdl'
          % (version, service), proxy=https_proxy, cache=self.cache,
          timeout=3600)
      self.assertIsInstance(suds_service, googleads.common.SudsServiceProxy)

    # Use the default server and https_proxy.
    self.dfa_client.https_proxy = None
    with mock.patch('suds.client.Client') as mock_client:
      suds_service = self.dfa_client.GetService(service, version)

      mock_client.assert_called_once_with(
          'https://advertisersapi.doubleclick.com/%s/api/dfa-api/%s?wsdl'
          % (version, service), proxy=None, cache=self.cache, timeout=3600)
      self.assertFalse(mock_client.return_value.set_options.called)
      self.assertIsInstance(suds_service, googleads.common.SudsServiceProxy)

  def testGetService_badService(self):
    version = googleads.dfa.DfaClient._SERVICE_MAP.keys()[0]
    with mock.patch('suds.client.Client') as mock_client:
      mock_client.side_effect = suds.transport.TransportError('', '')
      self.assertRaises(
          googleads.errors.GoogleAdsValueError, self.dfa_client.GetService,
          'GYIVyievfyiovslf', version)

  def testGetService_badVersion(self):
    with mock.patch('suds.client.Client') as mock_client:
      mock_client.side_effect = suds.transport.TransportError('', '')
      self.assertRaises(
          googleads.errors.GoogleAdsValueError, self.dfa_client.GetService,
          'campaign', '11111')

  def testGetService_transportError(self):
    version = googleads.dfa.DfaClient._SERVICE_MAP.keys()[0]
    service = googleads.dfa.DfaClient._SERVICE_MAP[version][0]
    with mock.patch('suds.client.Client') as mock_client:
      mock_client.side_effect = suds.transport.TransportError('', '')
      self.assertRaises(suds.transport.TransportError,
                        self.dfa_client.GetService, service, version)


if __name__ == '__main__':
  unittest.main()
