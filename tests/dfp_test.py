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

"""Unit tests to cover the dfp module."""

__author__ = 'Joseph DiLallo'

import StringIO
import sys
import unittest

import mock
import suds.transport

import googleads.dfp
import googleads.common
import googleads.errors


class DfpHeaderHandlerTest(unittest.TestCase):
  """Tests for the googleads.dfp._DfpHeaderHandler class."""

  def setUp(self):
    self.dfp_client = mock.Mock()
    self.header_handler = googleads.dfp._DfpHeaderHandler(self.dfp_client)

  def testSetHeaders(self):
    suds_client = mock.Mock()
    network_code = 'my network code is code'
    app_name = 'application name'
    oauth_header = {'oauth', 'header'}
    self.dfp_client.network_code = network_code
    self.dfp_client.application_name = app_name
    self.dfp_client.oauth2_client.CreateHttpHeader.return_value = oauth_header

    self.header_handler.SetHeaders(suds_client)

    # Check that the SOAP header has the correct values.
    suds_client.factory.create.assert_called_once_with('SoapRequestHeader')
    soap_header = suds_client.factory.create.return_value
    self.assertEqual(network_code, soap_header.networkCode)
    self.assertEqual(''.join([app_name,
                              googleads.dfp._DfpHeaderHandler._LIB_SIG]),
                     soap_header.applicationName)

    # Check that the suds client has the correct values.
    suds_client.set_options.assert_any_call(soapheaders=soap_header,
                                            headers=oauth_header)



class DfpClientTest(unittest.TestCase):
  """Tests for the googleads.dfp.DfpClient class."""

  def setUp(self):
    self.network_code = '12345'
    self.application_name = 'application name'
    self.oauth2_client = 'unused'
    self.https_proxy = 'myproxy.com:443'
    self.dfp_client = googleads.dfp.DfpClient(
        self.oauth2_client, self.application_name, self.network_code,
        self.https_proxy)

  def testLoadFromStorage(self):
    with mock.patch('googleads.common.LoadFromStorage') as mock_load:
      mock_load.return_value = {
          'network_code': 'abcdEFghIjkLMOpqRs',
          'oauth2_client': True,
          'application_name': 'unit testing'
      }
      self.assertIsInstance(googleads.dfp.DfpClient.LoadFromStorage(),
                            googleads.dfp.DfpClient)

  def testGetService_success(self):
    version = googleads.dfp._SERVICE_MAP.keys()[0]
    service = googleads.dfp._SERVICE_MAP[version][0]

    # Use a custom server. Also test what happens if the server ends with a
    # trailing slash
    server = 'https://testing.test.com/'
    https_proxy = {'https': self.https_proxy}
    with mock.patch('suds.client.Client') as mock_client:
      suds_service = self.dfp_client.GetService(service, version, server)

      mock_client.assert_called_once_with(
          'https://testing.test.com/apis/ads/publisher/%s/%s?wsdl'
          % (version, service))
      mock_client.return_value.set_options.assert_called_once_with(
          proxy=https_proxy)
      self.assertIsInstance(suds_service, googleads.common.SudsServiceProxy)

    # Use the default server and https proxy.
    self.dfp_client.https_proxy = None
    with mock.patch('suds.client.Client') as mock_client:
      suds_service = self.dfp_client.GetService(service, version)

      mock_client.assert_called_once_with(
          'https://www.google.com/apis/ads/publisher/%s/%s?wsdl'
          % (version, service))
      self.assertFalse(mock_client.return_value.set_options.called)
      self.assertIsInstance(suds_service, googleads.common.SudsServiceProxy)

  def testGetService_badService(self):
    version = googleads.dfp._SERVICE_MAP.keys()[0]
    with mock.patch('suds.client.Client') as mock_client:
      mock_client.side_effect = suds.transport.TransportError('', '')
      self.assertRaises(
          googleads.errors.GoogleAdsValueError, self.dfp_client.GetService,
          'GYIVyievfyiovslf', version)

  def testGetService_badVersion(self):
    with mock.patch('suds.client.Client') as mock_client:
      mock_client.side_effect = suds.transport.TransportError('', '')
      self.assertRaises(
          googleads.errors.GoogleAdsValueError, self.dfp_client.GetService,
          'CampaignService', '11111')

  def testGetService_transportError(self):
    version = googleads.dfp._SERVICE_MAP.keys()[0]
    service = googleads.dfp._SERVICE_MAP[version][0]
    with mock.patch('suds.client.Client') as mock_client:
      mock_client.side_effect = suds.transport.TransportError('', '')
      self.assertRaises(suds.transport.TransportError,
                        self.dfp_client.GetService, service, version)


class DataDownloaderTest(unittest.TestCase):
  """Tests for the googleads.dfp.DfpClient class."""

  def setUp(self):
    network_code = '12345'
    application_name = 'application name'
    oauth2_client = 'unused'
    https_proxy = 'myproxy.com:443'
    dfp_client = googleads.dfp.DfpClient(
        oauth2_client, application_name, network_code, https_proxy)
    self.report_downloader = dfp_client.GetDataDownloader()
    self.pql_service = mock.Mock()
    self.report_service = mock.Mock()
    self.report_downloader._pql_service = self.pql_service
    self.report_downloader._report_service = self.report_service

  def testDownloadPqlResultSetToCsv(self):
    csv_file = StringIO.StringIO()

    header = [{'labelName': 'Some random header...'},
              {'labelName': 'Another header...'}]
    rval = [{'values': [{'value': 'Some random PQL response...',
                         'Value.Type': 'TextValue'},
                        {'value': {'date': {
                            'year': '1999', 'month': '04', 'day': '03'}},
                         'Value.Type': 'DateValue'},
                        {'value': '123',
                         'Value.Type': 'NumberValue'},
                        {'value': {'date': {'year': '2012',
                                            'month': '11',
                                            'day': '05'},
                                   'hour': '12',
                                   'minute': '12',
                                   'second': '12',
                                   'timeZoneID': 'PST8PDT'},
                         'Value.Type': 'DateTimeValue'}]},
            {'values': [{'value': 'A second row of PQL response!',
                         'Value.Type': 'TextValue'},
                        {'value': {'date': {
                            'year': '2009', 'month': '02', 'day': '05'}},
                         'Value.Type': 'DateValue'},
                        {'value': '345',
                         'Value.Type': 'NumberValue'},
                        {'value': {'date': {'year': '2013',
                                            'month': '01',
                                            'day': '03'},
                                   'hour': '02',
                                   'minute': '02',
                                   'second': '02',
                                   'timeZoneID': 'GMT'},
                         'Value.Type': 'DateTimeValue'}]}]

    self.pql_service.select.return_value = {'rows': rval, 'columnTypes': header}

    self.report_downloader.DownloadPqlResultToCsv(
        'SELECT Id, Name FROM Line_Item', csv_file)

    csv_file.seek(0)
    self.assertEqual(csv_file.readline(),
                     ('"Some random header...",'
                      '"Another header..."\r\n'))
    self.assertEqual(csv_file.readline(),
                     ('"Some random PQL response...",'
                      '"1999-04-03",'
                      '123,'
                      '"2012-11-05T12:12:12-08:00"\r\n'))
    self.assertEqual(csv_file.readline(),
                     ('"A second row of PQL response!",'
                      '"2009-02-05",'
                      '345,'
                      '"2013-01-03T02:02:02Z"\r\n'))
    csv_file.close()

    self.pql_service.select.assert_called_once_with(
        {'values': None,
         'query': ('SELECT Id, Name FROM Line_Item LIMIT 500 OFFSET 0')})

  def testDownloadPqlResultToList(self):
    header = [{'labelName': 'Some random header...'},
              {'labelName': 'Another header...'}]
    rval = [{'values': [{'value': 'Some random PQL response...',
                         'Value.Type': 'TextValue'},
                        {'value': {'date': {
                            'year': '1999', 'month': '04', 'day': '03'}},
                         'Value.Type': 'DateValue'},
                        {'value': '123',
                         'Value.Type': 'NumberValue'},
                        {'value': {'date': {'year': '2012',
                                            'month': '11',
                                            'day': '05'},
                                   'hour': '12',
                                   'minute': '12',
                                   'second': '12',
                                   'timeZoneID': 'PST8PDT'},
                         'Value.Type': 'DateTimeValue'}]},
            {'values': [{'value': 'A second row of PQL response!',
                         'Value.Type': 'SomeUnknownValue'},
                        {'value': {'date': {
                            'year': '2009', 'month': '02', 'day': '05'}},
                         'Value.Type': 'DateValue'},
                        {'value': '345',
                         'Value.Type': 'NumberValue'},
                        {'value': {'date': {'year': '2013',
                                            'month': '01',
                                            'day': '03'},
                                   'hour': '02',
                                   'minute': '02',
                                   'second': '02',
                                   'timeZoneID': 'GMT'},
                         'Value.Type': 'DateTimeValue'}]}]

    self.pql_service.select.return_value = {'rows': rval, 'columnTypes': header}

    result_set = self.report_downloader.DownloadPqlResultToList(
        'SELECT Id, Name FROM Line_Item')

    row1 = [self.report_downloader._ConvertValueForCsv(field)
            for field in rval[0]['values']]
    row2 = [self.report_downloader._ConvertValueForCsv(field)
            for field in rval[1]['values']]

    self.pql_service.select.assert_called_once_with(
        {'values': None,
         'query': ('SELECT Id, Name FROM Line_Item LIMIT 500 OFFSET 0')})
    self.assertEqual([[header[0]['labelName'], header[1]['labelName']],
                      row1, row2], result_set)

  def testDownloadPqlResultToList_NoRows(self):
    self.pql_service.select.return_value = {}

    result_set = self.report_downloader.DownloadPqlResultToList(
        'SELECT Id, Name FROM Line_Item')

    self.pql_service.select.assert_called_once_with(
        {'values': None,
         'query': ('SELECT Id, Name FROM Line_Item LIMIT 500 OFFSET 0')})
    self.assertEqual([], result_set)

  def testWaitForReport_success(self):
    id_ = '1g684'
    input_ = {'query': 'something', 'id': id_}
    incomplete_response = {'reportJobStatus': 'PROCESSING', 'id': id_}
    complete_response = {'reportJobStatus': 'COMPLETED', 'id': id_}
    self.report_service.getReportJob.side_effect = [incomplete_response,
                                                    complete_response]
    self.report_service.runReportJob.return_value = input_

    with mock.patch('time.sleep') as mock_sleep:
      rval = self.report_downloader.WaitForReport(input_)
      mock_sleep.assert_called_once_with(30)
    self.assertEqual(id_, rval)
    self.report_service.getReportJob.assert_any_call(id_)

  def testWaitForReport_failure(self):
    self.report_service.getReportJob.return_value = {
        'reportJobStatus': 'FAILED'}
    self.report_service.runReportJob.return_value = {'id': '782yt97r2'}

    self.assertRaises(
        googleads.errors.DfpReportError,
        self.report_downloader.WaitForReport, {'id': 'obj'})

  def testDownloadReportToFile(self):
    report_format = 'csv'
    report_job_id = 't68t3278y429'
    report_download_url = 'http://google.com/something'
    report_contents = 'THIS IS YOUR REPORT!'
    fake_request = StringIO.StringIO()
    fake_request.write(report_contents)
    fake_request.seek(0)
    outfile = StringIO.StringIO()

    self.report_service.getReportDownloadURL.return_value = report_download_url

    with mock.patch('urllib2.urlopen' if sys.version_info[0] == 2
                    else 'urllib.request.urlopen') as mock_urlopen:
      mock_urlopen.return_value = fake_request
      self.report_downloader.DownloadReportToFile(
          report_job_id, report_format, outfile)
      mock_urlopen.assert_called_once_with(report_download_url)
      self.assertEqual(report_contents, outfile.getvalue())

  def testGetReportService(self):
    self.report_downloader._dfp_client = mock.Mock()
    self.report_downloader._report_service = None
    version = googleads.dfp._SERVICE_MAP.keys()[0]

    self.report_downloader._GetReportService()
    self.report_downloader._dfp_client.GetService.assert_called_once_with(
        'ReportService', version, 'https://www.google.com')

  def testGetPqlService(self):
    self.report_downloader._dfp_client = mock.Mock()
    self.report_downloader._pql_service = None
    version = googleads.dfp._SERVICE_MAP.keys()[0]

    self.report_downloader._GetPqlService()
    self.report_downloader._dfp_client.GetService.assert_called_once_with(
        'PublisherQueryLanguageService', version, 'https://www.google.com')


class FilterStatementTest(unittest.TestCase):
  """Tests for the FilterStatement class."""

  def testFilterStatement(self):
    values = [{
        'key': 'test_key',
        'value': {
            'xsi_type': 'TextValue',
            'value': 'test_value'
        }
    }]
    test_statement = googleads.dfp.FilterStatement()
    self.assertEqual(test_statement.ToStatement(),
                     {'query': ' LIMIT 500 OFFSET 0', 'values': None})
    test_statement.offset += 30
    self.assertEqual(test_statement.ToStatement(),
                     {'query': ' LIMIT 500 OFFSET 30', 'values': None})
    test_statement.offset = 123
    test_statement.limit = 5
    self.assertEqual(test_statement.ToStatement(),
                     {'query': ' LIMIT 5 OFFSET 123', 'values': None})
    test_statement = googleads.dfp.FilterStatement(
        'SELECT Id FROM Line_Item WHERE key = :test_key', limit=300, offset=20,
        values=values)
    self.assertEqual(test_statement.ToStatement(),
                     {'query': 'SELECT Id FROM Line_Item WHERE key = '
                               ':test_key LIMIT 300 OFFSET 20',
                      'values': values})


if __name__ == '__main__':
  unittest.main()
