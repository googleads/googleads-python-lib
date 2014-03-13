#!/usr/bin/python
# -*- coding: UTF-8 -*-
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

"""Unit tests to cover the adwords module."""

__author__ = 'Joseph DiLallo'

import io
import sys
import unittest
import urllib
import urllib2

import mock

import googleads.adwords
import googleads.common
import googleads.errors

PYTHON2 = sys.version_info[0] == 2
URL_REQUEST_PATH = ('urllib2' if PYTHON2 else 'urllib.request')


class AdWordsHeaderHandlerTest(unittest.TestCase):
  """Tests for the googleads.adwords._AdWordsHeaderHandler class."""

  def setUp(self):
    self.adwords_client = mock.Mock()
    self.header_handler = googleads.adwords._AdWordsHeaderHandler(
        self.adwords_client, 'v12345')

  def testSetHeaders(self):
    suds_client = mock.Mock()
    ccid = 'client customer id'
    dev_token = 'developer token'
    user_agent = 'user agent!'
    validate_only = True
    partial_failure = False
    oauth_header = {'oauth': 'header'}
    self.adwords_client.client_customer_id = ccid
    self.adwords_client.developer_token = dev_token
    self.adwords_client.user_agent = user_agent
    self.adwords_client.validate_only = validate_only
    self.adwords_client.partial_failure = partial_failure
    self.adwords_client.oauth2_client.CreateHttpHeader.return_value = (
        oauth_header)

    self.header_handler.SetHeaders(suds_client)

    # Check that the SOAP header has the correct values.
    suds_client.factory.create.assert_called_once_with(
        '{https://adwords.google.com/api/adwords/cm/v12345}SoapHeader')
    soap_header = suds_client.factory.create.return_value
    self.assertEqual(ccid, soap_header.clientCustomerId)
    self.assertEqual(dev_token, soap_header.developerToken)
    self.assertEqual(
        ''.join([user_agent, googleads.adwords._AdWordsHeaderHandler._LIB_SIG]),
        soap_header.userAgent)
    self.assertEqual(validate_only, soap_header.validateOnly)
    self.assertEqual(partial_failure, soap_header.partialFailure)

    # Check that the suds client has the correct values.
    suds_client.set_options.assert_any_call(
        soapheaders=soap_header, headers=oauth_header)

  def testGetReportDownloadHeaders(self):
    ccid = 'client customer id'
    dev_token = 'developer token'
    user_agent = 'user agent!'
    oauth_header = {'Authorization': 'header'}
    self.adwords_client.client_customer_id = ccid
    self.adwords_client.developer_token = dev_token
    self.adwords_client.user_agent = user_agent
    self.adwords_client.oauth2_client.CreateHttpHeader.return_value = dict(
        oauth_header)
    expected_return_value = {
        'Content-type': 'application/x-www-form-urlencoded',
        'developerToken': dev_token,
        'clientCustomerId': ccid,
        'returnMoneyInMicros': 'False',
        'Authorization': 'header',
        'User-Agent': ''.join([
            user_agent, googleads.adwords._AdWordsHeaderHandler._LIB_SIG,
            ',gzip'])
    }

    # Check that returnMoneyInMicros works when set to true.
    expected_return_value['returnMoneyInMicros'] = 'True'
    self.assertEqual(expected_return_value,
                     self.header_handler.GetReportDownloadHeaders(True))

    # Check that returnMoneyInMicros works when set to false.
    expected_return_value['returnMoneyInMicros'] = 'False'
    self.adwords_client.oauth2_client.CreateHttpHeader.return_value = dict(
        oauth_header)
    self.assertEqual(expected_return_value,
                     self.header_handler.GetReportDownloadHeaders(False))

    # Default returnMoneyInMicros value is not included in the headers.
    del expected_return_value['returnMoneyInMicros']
    self.adwords_client.oauth2_client.CreateHttpHeader.return_value = dict(
        oauth_header)
    self.assertEqual(expected_return_value,
                     self.header_handler.GetReportDownloadHeaders())


class AdWordsClientTest(unittest.TestCase):
  """Tests for the googleads.adwords.AdWordsClient class."""

  def setUp(self):
    self.dev_token = 'developers developers developers'
    self.user_agent = 'users users user'
    self.oauth2_client = 'unused'
    self.https_proxy = 'my.proxy:443'
    self.adwords_client = googleads.adwords.AdWordsClient(
        self.dev_token, self.oauth2_client, self.user_agent,
        https_proxy=self.https_proxy)

  def testLoadFromStorage(self):
    with mock.patch('googleads.common.LoadFromStorage') as mock_load:
      mock_load.return_value = {
          'developer_token': 'abcdEFghIjkLMOpqRs',
          'oauth2_client': True,
          'user_agent': 'unit testing'
      }
      self.assertIsInstance(googleads.adwords.AdWordsClient.LoadFromStorage(),
                            googleads.adwords.AdWordsClient)

  def testGetService_success(self):
    version = googleads.adwords._SERVICE_MAP.keys()[0]
    service = googleads.adwords._SERVICE_MAP[version].keys()[0]
    namespace = googleads.adwords._SERVICE_MAP[version][service]

    # Use a custom server. Also test what happens if the server ends with a
    # trailing slash
    server = 'https://testing.test.com/'
    https_proxy = {'https': self.https_proxy}
    with mock.patch('suds.client.Client') as mock_client:
      suds_service = self.adwords_client.GetService(service, version, server)

      mock_client.assert_called_once_with(
          'https://testing.test.com/api/adwords/%s/%s/%s?wsdl'
          % (namespace, version, service))
      mock_client.return_value.set_options.assert_called_once_with(
          proxy=https_proxy)
      self.assertIsInstance(suds_service, googleads.common.SudsServiceProxy)

    # Use the default server and https_proxy.
    self.adwords_client.https_proxy = None
    with mock.patch('suds.client.Client') as mock_client:
      suds_service = self.adwords_client.GetService(service, version)

      mock_client.assert_called_once_with(
          'https://adwords.google.com/api/adwords/%s/%s/%s?wsdl'
          % (namespace, version, service))
      self.assertFalse(mock_client.return_value.set_options.called)
      self.assertIsInstance(suds_service, googleads.common.SudsServiceProxy)

  def testGetService_badService(self):
    version = googleads.adwords._SERVICE_MAP.keys()[0]
    self.assertRaises(
        googleads.errors.GoogleAdsValueError, self.adwords_client.GetService,
        'GYIVyievfyiovslf', version)

  def testGetService_badVersion(self):
    self.assertRaises(
        googleads.errors.GoogleAdsValueError, self.adwords_client.GetService,
        'CampaignService', '11111')

  def testGetReportDownloader(self):
    with mock.patch('googleads.adwords.ReportDownloader') as mock_downloader:
      self.assertEqual(
          mock_downloader.return_value,
          self.adwords_client.GetReportDownloader('version', 'server'))
      mock_downloader.assert_called_once_with(
          self.adwords_client, 'version', 'server')


class ReportDownloaderTest(unittest.TestCase):
  """Tests for the googleads.adwords.ReportDownloader class."""

  def setUp(self):
    self.version = googleads.adwords._SERVICE_MAP.keys()[-1]
    self.marshaller = mock.Mock()
    self.header_handler = mock.Mock()
    self.adwords_client = mock.Mock()
    self.adwords_client.https_proxy = 'my.proxy.gov:443'
    with mock.patch('suds.client.Client'):
      with mock.patch('suds.xsd.doctor'):
        with mock.patch('suds.mx.literal.Literal') as mock_literal:
          with mock.patch(
              'googleads.adwords._AdWordsHeaderHandler') as mock_handler:
            mock_literal.return_value = self.marshaller
            mock_handler.return_value = self.header_handler
            self.report_downloader = googleads.adwords.ReportDownloader(
                self.adwords_client, self.version)

  def testDownloadReport(self):
    output_file = io.StringIO()
    report_definition = {'table': 'campaigns'}
    serialized_report = 'nuinbwuign'
    post_body = urllib.urlencode({'__rdxml': serialized_report})
    if not PYTHON2:
      post_body = bytes(post_body, 'utf-8')
    headers = {'Authorization': 'ya29.something'}
    self.header_handler.GetReportDownloadHeaders.return_value = headers
    content = u'CONTENT STRING 广告客户'
    fake_request = io.StringIO() if PYTHON2 else io.BytesIO()
    fake_request.write(content if PYTHON2 else bytes(content, 'utf-8'))
    fake_request.seek(0)
    self.marshaller.process.return_value = serialized_report

    with mock.patch('suds.mx.Content') as mock_content:
      with mock.patch(URL_REQUEST_PATH + '.urlopen') as mock_urlopen:
        with mock.patch(URL_REQUEST_PATH + '.Request') as mock_request:
          mock_urlopen.return_value = fake_request
          self.report_downloader.DownloadReport(
              report_definition, output_file, False)

          mock_request.assert_called_once_with(
              ('https://adwords.google.com/api/adwords/reportdownload/%s'
               % self.version), post_body, headers)
          mock_urlopen.assert_called_once_with(mock_request.return_value)
      self.marshaller.process.assert_called_once_with(mock_content.return_value)

    self.assertEqual(content, output_file.getvalue())
    self.header_handler.GetReportDownloadHeaders.assert_called_once_with(False)

  def testDownloadReport_failure(self):
    output_file = io.StringIO()
    report_definition = {'table': 'campaigns'}
    serialized_report = 'hjuibnibguo'
    post_body = urllib.urlencode({'__rdxml': serialized_report})
    if not PYTHON2:
      post_body = bytes(post_body, 'utf-8')
    headers = {'Authorization': 'ya29.something'}
    self.header_handler.GetReportDownloadHeaders.return_value = headers
    content = u'Page not found. :-('
    fake_request = io.StringIO() if PYTHON2 else io.BytesIO()
    fake_request.write(content if PYTHON2 else bytes(content, 'utf-8'))
    fake_request.seek(0)
    error = urllib2.HTTPError('', 400, 'Bad Request', {}, fp=fake_request)

    self.marshaller.process.return_value = serialized_report

    with mock.patch('suds.mx.Content') as mock_content:
      with mock.patch(URL_REQUEST_PATH + '.urlopen') as mock_urlopen:
        with mock.patch(URL_REQUEST_PATH + '.Request') as mock_request:
          mock_urlopen.side_effect = error
          self.assertRaises(
              googleads.errors.AdWordsReportError,
              self.report_downloader.DownloadReport, report_definition,
              output_file, True)

          mock_request.assert_called_once_with(
              ('https://adwords.google.com/api/adwords/reportdownload/%s'
               % self.version), post_body, headers)
          mock_urlopen.assert_called_once_with(mock_request.return_value)
      self.marshaller.process.assert_called_once_with(mock_content.return_value)

    self.assertEqual('', output_file.getvalue())
    self.header_handler.GetReportDownloadHeaders.assert_called_once_with(True)

  def testDownloadReportWithAwql(self):
    output_file = io.StringIO()
    query = 'SELECT Id FROM Campaign WHERE NAME LIKE \'%Test%\''
    file_format = 'CSV'
    post_body = urllib.urlencode({'__fmt': file_format, '__rdquery': query})
    if not PYTHON2:
      post_body = bytes(post_body, 'utf-8')
    headers = {'Authorization': 'ya29.something'}
    self.header_handler.GetReportDownloadHeaders.return_value = headers
    content = u'CONTENT STRING'
    fake_request = io.StringIO() if PYTHON2 else io.BytesIO()
    fake_request.write(content if PYTHON2 else bytes(content, 'utf-8'))
    fake_request.seek(0)

    with mock.patch(URL_REQUEST_PATH + '.urlopen') as mock_urlopen:
      with mock.patch(URL_REQUEST_PATH + '.Request') as mock_request:
        mock_urlopen.return_value = fake_request
        self.report_downloader.DownloadReportWithAwql(
            query, file_format, output_file, True)

        mock_request.assert_called_once_with(
            ('https://adwords.google.com/api/adwords/reportdownload/%s'
             % self.version), post_body, headers)
        mock_urlopen.assert_called_once_with(mock_request.return_value)

    self.assertEqual(content, output_file.getvalue())
    self.header_handler.GetReportDownloadHeaders.assert_called_once_with(True)

  def testExtractError_badRequest(self):
    response = mock.Mock()
    response.code = 400
    type_ = 'ReportDownloadError.INVALID_REPORT_DEFINITION_XML'
    trigger = 'Invalid enumeration.'
    field_path = 'Criteria.Type'
    content_template = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<reportDownloadError><ApiError><type>%s</type><trigger>%s</trigger>'
        '<fieldPath>%s</fieldPath></ApiError></reportDownloadError>')
    content = content_template % (type_, trigger, field_path)
    response.read.return_value = (content if PYTHON2
                                  else bytes(content, 'utf-8'))

    rval = self.report_downloader._ExtractError(response)
    self.assertEqual(type_, rval.type)
    self.assertEqual(trigger, rval.trigger)
    self.assertEqual(field_path, rval.field_path)
    self.assertEqual(response.code, rval.code)
    self.assertEqual(response, rval.error)
    self.assertEqual(content, rval.content)
    self.assertIsInstance(rval, googleads.errors.AdWordsReportBadRequestError)

    # Check that if the XML fields are empty, this still functions.
    content = content_template % ('', '', '')
    response.read.return_value = (content if PYTHON2
                                  else bytes(content, 'utf-8'))
    rval = self.report_downloader._ExtractError(response)
    self.assertEqual(None, rval.type)
    self.assertEqual(None, rval.trigger)
    self.assertEqual(None, rval.field_path)

  def testExtractError_malformedBadRequest(self):
    response = mock.Mock()
    response.code = 400
    content = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
               '<reportDownloadError><ApiError><type>1234</type><trigger>5678'
               '</trigger></ApiError></ExtraElement></reportDownloadError>')
    response.read.return_value = (content if PYTHON2
                                  else bytes(content, 'utf-8'))

    rval = self.report_downloader._ExtractError(response)
    self.assertEqual(response.code, rval.code)
    self.assertEqual(response, rval.error)
    self.assertEqual(content, rval.content)
    self.assertIsInstance(rval, googleads.errors.AdWordsReportError)

  def testExtractError_notBadRequest(self):
    response = mock.Mock()
    response.code = 400
    content = 'Page not found!'
    response.read.return_value = (content if PYTHON2
                                  else bytes(content, 'utf-8'))

    rval = self.report_downloader._ExtractError(response)
    self.assertEqual(response.code, rval.code)
    self.assertEqual(response, rval.error)
    self.assertEqual(content, rval.content)
    self.assertIsInstance(rval, googleads.errors.AdWordsReportError)


if __name__ == '__main__':
  unittest.main()
