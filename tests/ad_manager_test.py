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

"""Unit tests to cover the ad_manager module."""


import datetime
import unittest

import mock
import pytz
import io
import googleads.ad_manager
import googleads.common
import googleads.errors
from . import testing


CURRENT_VERSION = sorted(googleads.ad_manager._SERVICE_MAP.keys())[-1]


class BaseValue(object):

  def __init__(self, original_object):
    self.original_object = original_object

  def __getitem__(self, key):
    return self.original_object[key]

  def __contains__(self, key):
    if key in self.original_object:
      return True
    return False


class TextValue(BaseValue):

  def __init__(self, original_object):
    BaseValue.__init__(self, original_object)


class NumberValue(BaseValue):

  def __init__(self, original_object):
    BaseValue.__init__(self, original_object)


class DateValue(BaseValue):

  def __init__(self, original_object):
    BaseValue.__init__(self, original_object)


class DateTimeValue(BaseValue):

  def __init__(self, original_object):
    BaseValue.__init__(self, original_object)


class BooleanValue(BaseValue):

  def __init__(self, original_object):
    BaseValue.__init__(self, original_object)


class SetValue(object):

  def __init__(self, original_object):
    packed_objects = [DecideValue(obj_to_pack) for obj_to_pack
                      in original_object['values']]
    self.original_object = {'values': packed_objects}

  def __getitem__(self, key):
    return self.original_object[key]

  def __contains__(self, key):
    if key in self.original_object:
      return True
    return False


def DecideValue(original_object):
  class_type = original_object['xsi_type']
  if class_type == 'TextValue':
    return TextValue(original_object)
  elif class_type == 'NumberValue':
    return NumberValue(original_object)
  elif class_type == 'DateValue':
    return DateValue(original_object)
  elif class_type == 'DateTimeValue':
    return DateTimeValue(original_object)
  elif class_type == 'SetValue':
    return SetValue(original_object)
  else:
    return BooleanValue(original_object)


class AdManagerHeaderHandlerTest(testing.CleanUtilityRegistryTestCase):
  """Tests for the googleads.ad_manager._AdManagerHeaderHandler class."""

  def setUp(self):
    self.ad_manager_client = mock.Mock()
    self.enable_compression = False
    self.custom_headers = ()
    self.header_handler = googleads.ad_manager._AdManagerHeaderHandler(
        self.ad_manager_client, self.enable_compression, self.custom_headers)
    self.utility_name = 'TestUtility'
    self.default_sig_template = ' (%s, %s, %s)'
    self.util_sig_template = ' (%s, %s, %s, %s)'
    self.network_code = 'my network code is code'
    self.app_name = 'application name'
    self.oauth_header = {'oauth': 'header'}

    @googleads.common.RegisterUtility(self.utility_name)
    class TestUtility(object):

      def Test(self):
        pass

    self.test_utility = TestUtility()

  def testGetHTTPHeaders(self):
    self.ad_manager_client.oauth2_client.CreateHttpHeader.return_value = (
        self.oauth_header)

    header_result = self.header_handler.GetHTTPHeaders()

    # Check that the returned headers have the correct values.
    self.assertEqual(header_result, self.oauth_header)

  def testGetHTTPHeadersWithCustomHeaders(self):
    self.ad_manager_client.oauth2_client.CreateHttpHeader.return_value = (
        self.oauth_header)
    self.header_handler.custom_http_headers = {'X-My-Header': 'abc'}

    header_result = self.header_handler.GetHTTPHeaders()

    # Check that the returned headers have the correct values.
    self.assertEqual(header_result, {'oauth': 'header', 'X-My-Header': 'abc'})

  def testGetSOAPHeaders(self):
    create_method = mock.Mock()
    self.ad_manager_client.network_code = self.network_code
    self.ad_manager_client.application_name = self.app_name

    header_result = self.header_handler.GetSOAPHeaders(create_method)

    # Check that the SOAP header has the correct values.
    create_method.assert_called_once_with('ns0:SoapRequestHeader')
    self.assertEqual(self.network_code, header_result.networkCode)
    self.assertEqual(
        ''.join([
            self.app_name,
            googleads.common.GenerateLibSig(
                googleads.ad_manager._AdManagerHeaderHandler._PRODUCT_SIG)]),
        header_result.applicationName)

  def testGetSOAPHeadersUserAgentWithUtility(self):
    create_method = mock.Mock()
    self.ad_manager_client.network_code = self.network_code
    self.ad_manager_client.application_name = self.app_name

    with mock.patch('googleads.common._COMMON_LIB_SIG') as mock_common_sig:
      with mock.patch('googleads.common._PYTHON_VERSION') as mock_py_ver:
        self.test_utility.Test()  # This will register TestUtility.
        soap_header = self.header_handler.GetSOAPHeaders(create_method)
        self.assertEqual(
            ''.join([
                self.app_name,
                self.util_sig_template % (
                    googleads.ad_manager._AdManagerHeaderHandler._PRODUCT_SIG,
                    mock_common_sig,
                    mock_py_ver,
                    self.utility_name)]),
            soap_header.applicationName)

  def testGetHeadersUserAgentWithAndWithoutUtility(self):
    create_method = mock.Mock()

    self.ad_manager_client.network_code = self.network_code
    self.ad_manager_client.application_name = self.app_name

    with mock.patch('googleads.common._COMMON_LIB_SIG') as mock_common_sig:
      with mock.patch('googleads.common._PYTHON_VERSION') as mock_py_ver:
        # Check headers when utility registered.
        self.test_utility.Test()  # This will register TestUtility.
        soap_header = self.header_handler.GetSOAPHeaders(create_method)
        self.assertEqual(
            ''.join([
                self.app_name,
                self.util_sig_template % (
                    googleads.ad_manager._AdManagerHeaderHandler._PRODUCT_SIG,
                    mock_common_sig,
                    mock_py_ver,
                    self.utility_name)]),
            soap_header.applicationName)

        # Check headers when no utility should be registered.
        soap_header = self.header_handler.GetSOAPHeaders(create_method)
        self.assertEqual(
            ''.join([
                self.app_name,
                self.default_sig_template % (
                    googleads.ad_manager._AdManagerHeaderHandler._PRODUCT_SIG,
                    mock_common_sig,
                    mock_py_ver)]),
            soap_header.applicationName)

        # Verify that utility is registered in subsequent uses.
        self.test_utility.Test()  # This will register TestUtility.
        soap_header = self.header_handler.GetSOAPHeaders(create_method)
        self.assertEqual(
            ''.join([
                self.app_name,
                self.util_sig_template % (
                    googleads.ad_manager._AdManagerHeaderHandler._PRODUCT_SIG,
                    mock_common_sig,
                    mock_py_ver,
                    self.utility_name)]),
            soap_header.applicationName)


class AdManagerClientTest(unittest.TestCase):
  """Tests for the googleads.ad_manager.AdManagerClient class."""

  def setUp(self):
    self.network_code = '12345'
    self.application_name = 'application name'
    self.oauth2_client = mock.Mock()
    self.oauth2_client.CreateHttpHeader.return_value = {}
    self.proxy_host = 'myproxy'
    self.proxy_port = 443
    self.https_proxy = 'http://myproxy:443'
    self.proxy_config = googleads.common.ProxyConfig(
        https_proxy=self.https_proxy)
    self.cache = None
    self.version = sorted(googleads.ad_manager._SERVICE_MAP.keys())[-1]

  def CreateAdManagerClient(self, **kwargs):
    if 'proxy_config' not in kwargs:
      kwargs['proxy_config'] = self.proxy_config

    if 'cache' not in kwargs:
      kwargs['cache'] = self.cache

    return googleads.ad_manager.AdManagerClient(
        self.oauth2_client, self.application_name, self.network_code,
        **kwargs)

  def testLoadFromString(self):
    with mock.patch('googleads.common.LoadFromString') as mock_load:
      mock_load.return_value = {
          'network_code': 'abcdEFghIjkLMOpqRs',
          'oauth2_client': True,
          'application_name': 'unit testing'
      }
      self.assertIsInstance(
          googleads.ad_manager.AdManagerClient.LoadFromString(''),
          googleads.ad_manager.AdManagerClient)

  def testLoadFromStorage(self):
    with mock.patch('googleads.common.LoadFromStorage') as mock_load:
      mock_load.return_value = {
          'network_code': 'abcdEFghIjkLMOpqRs',
          'oauth2_client': True,
          'application_name': 'unit testing'
      }
      self.assertIsInstance(
          googleads.ad_manager.AdManagerClient.LoadFromStorage(),
          googleads.ad_manager.AdManagerClient)

  def testLoadFromStorageWithCompressionEnabled(self):
    enable_compression = True
    application_name_gzip_template = '%s (gzip)'
    default_app_name = 'unit testing'
    custom_headers = {'X-My-Header': 'abc'}

    with mock.patch('googleads.common.LoadFromStorage') as mock_load:
      with mock.patch('googleads.ad_manager._AdManagerHeaderHandler') as mock_h:
        mock_load.return_value = {
            'network_code': 'abcdEFghIjkLMOpqRs',
            'oauth2_client': True,
            'application_name': default_app_name,
            'enable_compression': enable_compression,
            'custom_http_headers': custom_headers
        }
        ad_manager = googleads.ad_manager.AdManagerClient.LoadFromStorage()
        self.assertEqual(
            application_name_gzip_template % default_app_name,
            ad_manager.application_name)
        mock_h.assert_called_once_with(
            ad_manager, enable_compression, custom_headers)

  def testInitializeWithDefaultApplicationName(self):
    self.application_name = 'INSERT_APPLICATION_NAME_HERE'
    self.assertRaises(
        googleads.errors.GoogleAdsValueError,
        googleads.ad_manager.AdManagerClient, self.oauth2_client,
        self.application_name, self.network_code, self.https_proxy, self.cache)

  def testInitializeWithUselessApplicationName(self):
    self.application_name = 'try_to_trick_me_INSERT_APPLICATION_NAME_HERE'
    self.assertRaises(
        googleads.errors.GoogleAdsValueError,
        googleads.ad_manager.AdManagerClient, self.oauth2_client,
        self.application_name, self.network_code, self.https_proxy, self.cache)

  def testGetService_success(self):
    ad_manager = self.CreateAdManagerClient(
        cache='cache', proxy_config='proxy', timeout='timeout')
    service_name = googleads.ad_manager._SERVICE_MAP[self.version][0]

    # Use a custom server. Also test what happens if the server ends with a
    # trailing slash
    server = 'https://testing.test.com/'
    with mock.patch('googleads.common.'
                    'GetServiceClassForLibrary') as mock_get_service:
      impl = mock.Mock()
      mock_service = mock.Mock()
      impl.return_value = mock_service
      mock_get_service.return_value = impl

      service = ad_manager.GetService(service_name, self.version, server)

      impl.assert_called_once_with(
          'https://testing.test.com/apis/ads/publisher/%s/%s?wsdl'
          % (self.version, service_name), ad_manager._header_handler,
          googleads.ad_manager._AdManagerPacker, 'proxy', 'timeout',
          self.version, cache='cache')
      self.assertEqual(service, mock_service)


  def testGetService_badService(self):
    ad_manager = self.CreateAdManagerClient()
    with mock.patch('googleads.common.'
                    'GetServiceClassForLibrary') as mock_get_service:
      mock_get_service.side_effect = (
          googleads.errors.GoogleAdsSoapTransportError('', ''))
      self.assertRaises(
          googleads.errors.GoogleAdsValueError, ad_manager.GetService,
          'GYIVyievfyiovslf', self.version)

  def testGetService_badVersion(self):
    ad_manager = self.CreateAdManagerClient()
    with mock.patch('googleads.common.'
                    'GetServiceClassForLibrary') as mock_get_service:
      mock_get_service.side_effect = (
          googleads.errors.GoogleAdsSoapTransportError('', ''))
      self.assertRaises(
          googleads.errors.GoogleAdsValueError, ad_manager.GetService,
          'CampaignService', '11111')

  def testGetService_transportError(self):
    service = googleads.ad_manager._SERVICE_MAP[self.version][0]
    ad_manager = self.CreateAdManagerClient()
    with mock.patch('googleads.common.'
                    'GetServiceClassForLibrary') as mock_get_service:
      mock_get_service.side_effect = (
          googleads.errors.GoogleAdsSoapTransportError('', ''))
      self.assertRaises(googleads.errors.GoogleAdsSoapTransportError,
                        ad_manager.GetService, service, self.version)


class AdManagerPackerTest(unittest.TestCase):
  """Tests for the googleads.ad_manager._AdManagerPacker class."""

  def setUp(self):
    self.packer = googleads.ad_manager._AdManagerPacker

  def testPackDate(self):
    input_date = datetime.date(2017, 1, 2)
    result = self.packer.Pack(input_date, CURRENT_VERSION)
    self.assertEqual(result, {'year': 2017, 'month': 1, 'day': 2})

  def testPackDateTime(self):
    input_date = datetime.datetime(2017, 1, 2, 3, 4, 5)
    input_date = pytz.timezone('America/New_York').localize(input_date)
    result = self.packer.Pack(input_date, CURRENT_VERSION)
    self.assertEqual(result, {'date': {'year': 2017, 'month': 1, 'day': 2},
                              'hour': 3, 'minute': 4, 'second': 5,
                              'timeZoneId': 'America/New_York'})

  def testPackDateTimeNeedsTimeZone(self):
    input_date = datetime.datetime(2017, 1, 2, 3, 4, 5)
    self.assertRaises(googleads.errors.GoogleAdsValueError,
                      self.packer.Pack, input_date, CURRENT_VERSION)

  def testPackUnsupportedObjectType(self):
    obj = object()
    self.assertEqual(googleads.ad_manager._AdManagerPacker.
                     Pack(obj, CURRENT_VERSION), obj)


class DataDownloaderTest(unittest.TestCase):
  """Tests for the googleads.ad_manager.AdManagerClient class."""

  def setUp(self):
    network_code = '12345'
    application_name = 'application name'
    oauth2_client = 'unused'
    self.https_proxy = 'myproxy.com:443'
    self.ad_manager = googleads.ad_manager.AdManagerClient(
        oauth2_client, application_name, network_code, self.https_proxy)
    self.version = sorted(googleads.ad_manager._SERVICE_MAP.keys())[-1]
    self.report_downloader = self.ad_manager.GetDataDownloader()
    self.pql_service = mock.Mock()
    self.report_service = mock.Mock()
    self.report_downloader._pql_service = self.pql_service
    self.report_downloader._report_service = self.report_service
    self.generic_header = [{'labelName': 'Some random header...'},
                           {'labelName': 'Another header...'}]

    row1_field1 = {
        'value': 'Some random PQL response...',
        'xsi_type': 'TextValue'
    }

    row1_field2 = {
        'value': {
            'date': {
                'year': '1999', 'month': '04', 'day': '03'}
            },
        'xsi_type': 'DateValue'
    }

    row1_field3 = {
        'value': '123',
        'xsi_type': 'NumberValue'
    }

    row1_field4 = {
        'value': {
            'date': {
                'year': '2012',
                'month': '11',
                'day': '05'
            },
            'hour': '12',
            'minute': '12',
            'second': '12',
            'timeZoneId': 'PST8PDT'},
        'xsi_type': 'DateTimeValue'
    }

    row1_field5 = {
        'value': None,
        'xsi_type': 'NumberValue'
    }

    row1_field6 = {
        'values': [{
            'value': 'Whatcha thinkin about?',
            'xsi_type': 'TextValue'
        }, {
            'value': 'Oh nothing, just String stuff...',
            'xsi_type': 'TextValue'
        }],
        'xsi_type': 'SetValue'
    }

    row2_field1 = {
        'value': 'A second row of PQL response!',
        'xsi_type': 'TextValue'
    }

    row2_field2 = {
        'value': {
            'date': {
                'year': '2009',
                'month': '02',
                'day': '05'
            }
        },
        'xsi_type': 'DateValue'
    }

    row2_field3 = {
        'value': '345',
        'xsi_type': 'NumberValue'
    }

    row2_field4 = {
        'value': {
            'date': {
                'year': '2013',
                'month': '01',
                'day': '03'
            },
            'hour': '02',
            'minute': '02',
            'second': '02',
            'timeZoneId': 'GMT'
        },
        'xsi_type': 'DateTimeValue'
    }

    row2_field5 = {
        'value': '123456',
        'xsi_type': 'NumberValue'
    }

    row2_field6 = {
        'values': [{
            'value': 'Look at how many commas and "s there are',
            'xsi_type': 'TextValue'
        }, {
            'value': 'this,is...how,Christopher Walken, talks',
            'xsi_type': 'TextValue'
        }],
        'xsi_type': 'SetValue'
    }

    row1 = [row1_field1, row1_field2, row1_field3, row1_field4, row1_field5,
            row1_field6]
    row2 = [row2_field1, row2_field2, row2_field3, row2_field4, row2_field5,
            row2_field6]

    self.generic_rval = [{
        'values': [DecideValue(value) for value in row1]
    }, {
        'values': [DecideValue(value) for value in row2]
    }]

  def testDownloadPqlResultSetToCsv(self):
    csv_file = io.StringIO()

    self.pql_service.select.return_value = {'rows': self.generic_rval,
                                            'columnTypes': self.generic_header}

    self.report_downloader.DownloadPqlResultToCsv(
        'SELECT Id, Name FROM Line_Item', csv_file)

    csv_file.seek(0)
    self.assertEqual(csv_file.readline(),
                     ('"Some random header...",'
                      '"Another header..."\r\n'))
    self.assertEqual(csv_file.readline(),
                     ('"Some random PQL response...",'
                      '"1999-04-03",'
                      '"123",'
                      '"2012-11-05T12:12:12-08:00",'
                      '"-","""Whatcha thinkin about?"",""Oh nothing, '
                      'just String stuff..."""\r\n'))
    self.assertEqual(csv_file.readline(),
                     ('"A second row of PQL response!",'
                      '"2009-02-05",'
                      '"345",'
                      '"2013-01-03T02:02:02Z",'
                      '"123456","""Look at how many commas and """"s there are'
                      '"",""this,is...how,Christopher Walken, talks"""\r\n'))
    csv_file.close()

    self.pql_service.select.assert_called_once_with(
        {'values': None,
         'query': ('SELECT Id, Name FROM Line_Item LIMIT 500 OFFSET 0')})

  def testDownloadPqlResultToList(self):
    self.pql_service.select.return_value = {'rows': self.generic_rval,
                                            'columnTypes': self.generic_header}

    result_set = self.report_downloader.DownloadPqlResultToList(
        'SELECT Id, Name FROM Line_Item')

    row1 = [self.report_downloader._ConvertValueForCsv(field)
            for field in self.generic_rval[0]['values']]
    row2 = [self.report_downloader._ConvertValueForCsv(field)
            for field in self.generic_rval[1]['values']]

    self.pql_service.select.assert_called_once_with(
        {'values': None,
         'query': ('SELECT Id, Name FROM Line_Item LIMIT 500 OFFSET 0')})
    self.assertEqual([[self.generic_header[0]['labelName'],
                       self.generic_header[1]['labelName']],
                      row1, row2], result_set)

  def testDownloadPqlResultToListWithOldValuesList(self):
    self.pql_service.select.return_value = {'rows': self.generic_rval,
                                            'columnTypes': self.generic_header}

    result_set = self.report_downloader.DownloadPqlResultToList(
        'SELECT Id, Name FROM Line_Item WHERE Id = :id',
        [{'key': 'id', 'value': {'xsi_type': 'NumberValue', 'value': 1}}])

    row1 = [self.report_downloader._ConvertValueForCsv(field)
            for field in self.generic_rval[0]['values']]
    row2 = [self.report_downloader._ConvertValueForCsv(field)
            for field in self.generic_rval[1]['values']]

    self.pql_service.select.assert_called_once_with(
        {'values': [{'key': 'id',
                     'value': {'xsi_type': 'NumberValue', 'value': 1}}],
         'query': ('SELECT Id, Name FROM Line_Item '
                   'WHERE Id = :id LIMIT 500 OFFSET 0')})
    self.assertEqual([[self.generic_header[0]['labelName'],
                       self.generic_header[1]['labelName']],
                      row1, row2], result_set)

  def testDownloadPqlResultToListWithDict(self):
    self.pql_service.select.return_value = {'rows': self.generic_rval,
                                            'columnTypes': self.generic_header}

    result_set = self.report_downloader.DownloadPqlResultToList(
        'SELECT Id, Name FROM Line_Item WHERE Id = :id',
        {'id': 1})

    row1 = [self.report_downloader._ConvertValueForCsv(field)
            for field in self.generic_rval[0]['values']]
    row2 = [self.report_downloader._ConvertValueForCsv(field)
            for field in self.generic_rval[1]['values']]

    self.pql_service.select.assert_called_once_with(
        {'values': [{'key': 'id',
                     'value': {'xsi_type': 'NumberValue', 'value': 1}}],
         'query': ('SELECT Id, Name FROM Line_Item '
                   'WHERE Id = :id LIMIT 500 OFFSET 0')})
    self.assertEqual([[self.generic_header[0]['labelName'],
                       self.generic_header[1]['labelName']],
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
    input_ = {'reportQuery': 'something', 'id': id_}
    self.report_service.getReportJobStatus.side_effect = ['IN_PROGRESS',
                                                          'COMPLETED']
    self.report_service.runReportJob.return_value = input_

    with mock.patch('time.sleep') as mock_sleep:
      rval = self.report_downloader.WaitForReport(input_)
      mock_sleep.assert_called_once_with(30)
    self.assertEqual(id_, rval)
    self.report_service.getReportJobStatus.assert_any_call(id_)

  def testWaitForReport_failure(self):
    self.report_service.getReportJobStatus.return_value = 'FAILED'
    self.report_service.runReportJob.return_value = {'id': '782yt97r2'}

    self.assertRaises(
        googleads.errors.AdManagerReportError,
        self.report_downloader.WaitForReport, {'id': 'obj'})

  def testDownloadReportToFile(self):
    report_format = 'CSV_DUMP'
    report_job_id = 't68t3278y429'
    report_download_url = 'http://google.com/something'
    report_data = 'THIS IS YOUR REPORT!'
    report_contents = io.StringIO()
    report_contents.write(report_data)
    report_contents.seek(0)
    fake_response = mock.Mock()
    fake_response.read = report_contents.read
    fake_response.msg = 'fake message'
    fake_response.code = '200'
    outfile = io.StringIO()

    download_func = self.report_service.getReportDownloadUrlWithOptions
    download_func.return_value = report_download_url

    with mock.patch('urllib.request.OpenerDirector.open') as mock_open:
      mock_open.return_value = fake_response

      self.report_downloader.DownloadReportToFile(
          report_job_id, report_format, outfile)
      default_opts = {
          'exportFormat': report_format,
          'includeReportProperties': False,
          'includeTotalsRow': False,
          'useGzipCompression': True,
      }
      download_func.assert_called_once_with(report_job_id, default_opts)
      mock_open.assert_called_once_with(report_download_url)
      self.assertEqual(report_data, outfile.getvalue())

  def testGetReportService(self):
    self.report_downloader._ad_manager_client = mock.Mock()
    self.report_downloader._report_service = None

    self.report_downloader._GetReportService()
    client = self.report_downloader._ad_manager_client
    client.GetService.assert_called_once_with(
        'ReportService', self.version, 'https://ads.google.com')

  def testGetPqlService(self):
    self.report_downloader._ad_manager_client = mock.Mock()
    self.report_downloader._pql_service = None

    self.report_downloader._GetPqlService()
    client = self.report_downloader._ad_manager_client
    client.GetService.assert_called_once_with(
        'PublisherQueryLanguageService', self.version, 'https://ads.google.com')

  def testDownloadHasCustomHeaders(self):
    self.ad_manager.custom_http_headers = {'X-My-Headers': 'abc'}

    class MyOpener(object):
      addheaders = [('a', 'b')]
    opener = MyOpener()

    with mock.patch('googleads.ad_manager.build_opener') as mock_build_opener:
      mock_build_opener.return_value = opener

      self.ad_manager.GetDataDownloader()
      self.assertEqual(opener.addheaders, [('a', 'b'), ('X-My-Headers', 'abc')])


class StatementBuilderTest(testing.CleanUtilityRegistryTestCase):
  """Tests for the StatementBuilder class."""

  def testBuildBasicSelectFrom(self):
    test_statement = googleads.ad_manager.StatementBuilder()
    select_call_result = test_statement.Select('Id')
    from_call_result = test_statement.From('Line_Item')

    self.assertEqual(select_call_result, test_statement)
    self.assertEqual(from_call_result, test_statement)
    self.assertEqual(test_statement.ToStatement(),
                     {'query': ('SELECT Id FROM Line_Item LIMIT %s OFFSET 0' %
                                googleads.ad_manager.SUGGESTED_PAGE_LIMIT),
                      'values': None})

  def testLimitClause(self):
    test_statement = googleads.ad_manager.StatementBuilder()
    limit_call_result = (test_statement
                         .Select('Id')
                         .From('Line_Item')
                         .Limit(5))

    self.assertEqual(limit_call_result, test_statement)
    self.assertEqual(test_statement.ToStatement(),
                     {'query': 'SELECT Id FROM Line_Item LIMIT 5 OFFSET 0',
                      'values': None})

    limit_call_result.Limit(None)
    self.assertEqual(test_statement.ToStatement(),
                     {'query': 'SELECT Id FROM Line_Item OFFSET 0',
                      'values': None})

  def testOffsetClause(self):
    test_statement = googleads.ad_manager.StatementBuilder()
    offset_call_result = (
        test_statement
        .Select('Id')
        .From('Line_Item')
        .Offset(100)
    )

    self.assertEqual(offset_call_result, test_statement)
    self.assertEqual(test_statement.ToStatement(),
                     {'query': ('SELECT Id FROM Line_Item LIMIT %s OFFSET 100' %
                                googleads.ad_manager.SUGGESTED_PAGE_LIMIT),
                      'values': None})

  def testOrderByClause(self):
    test_statement = googleads.ad_manager.StatementBuilder()
    order_call_result = (
        test_statement
        .Select('Id')
        .From('Line_Item')
        .OrderBy('Id')
    )

    self.assertEqual(order_call_result, test_statement)
    self.assertEqual(test_statement.ToStatement(),
                     {'query': ('SELECT Id FROM Line_Item '
                                'ORDER BY Id ASC '
                                'LIMIT %s OFFSET 0' %
                                googleads.ad_manager.SUGGESTED_PAGE_LIMIT),
                      'values': None})

    test_statement.OrderBy('Id', ascending=False)
    self.assertEqual(test_statement.ToStatement(),
                     {'query': ('SELECT Id FROM Line_Item '
                                'ORDER BY Id DESC '
                                'LIMIT %s OFFSET 0' %
                                googleads.ad_manager.SUGGESTED_PAGE_LIMIT),
                      'values': None})

  def testConstructorArgs(self):
    test_statement = googleads.ad_manager.StatementBuilder(
        select_columns='Id', from_table='Line_Item', where='abc = 123',
        order_by='Id', order_ascending=False)

    self.assertEqual(test_statement.ToStatement(),
                     {'query': ('SELECT Id FROM Line_Item '
                                'WHERE abc = 123 '
                                'ORDER BY Id DESC '
                                'LIMIT %s OFFSET 0' %
                                googleads.ad_manager.SUGGESTED_PAGE_LIMIT),
                      'values': None})

  def testWhereWithStringVariable(self):
    test_statement = googleads.ad_manager.StatementBuilder()
    where_call_result = (
        test_statement
        .Select('Id')
        .From('Line_Item')
        .Where('key = :test_key')
    )
    bind_call_result = test_statement.WithBindVariable('test_key', 'test_value')

    target_values = [{
        'key': 'test_key',
        'value': {
            'xsi_type': 'TextValue',
            'value': 'test_value'
        }
    }]
    self.assertEqual(where_call_result, test_statement)
    self.assertEqual(bind_call_result, test_statement)
    self.assertEqual(
        test_statement.ToStatement(),
        {'query': (
            'SELECT Id FROM Line_Item '
            'WHERE key = :test_key '
            'LIMIT %s '
            'OFFSET 0' % googleads.ad_manager.SUGGESTED_PAGE_LIMIT),
         'values': target_values})

  def testWhereWithOtherTypes(self):
    test_statement = googleads.ad_manager.StatementBuilder()
    test_statement.Where((
        'bool_key = :test_bool_key '
        'AND number_key = :test_number_key '
        'AND date_key = :test_date_key '
        'AND datetime_key = :test_datetime_key '
        'AND set_key = :test_set_key'
    ))

    test_statement.WithBindVariable('test_bool_key', True)
    test_statement.WithBindVariable('test_number_key', 5)
    test_statement.WithBindVariable('test_date_key', datetime.date(2017, 1, 2))
    test_dt = datetime.datetime(2017, 1, 2,
                                hour=3, minute=4, second=5,
                               )
    test_dt = pytz.timezone('America/New_York').localize(test_dt)
    test_statement.WithBindVariable('test_datetime_key', test_dt)
    test_statement.WithBindVariable('test_set_key', [1, 2])

    target_values = [{
        'key': 'test_bool_key',
        'value': {
            'xsi_type': 'BooleanValue',
            'value': True,
        }
    }, {
        'key': 'test_number_key',
        'value': {
            'xsi_type': 'NumberValue',
            'value': 5,
        }
    }, {
        'key': 'test_date_key',
        'value': {
            'xsi_type': 'DateValue',
            'value': {
                'year': 2017,
                'month': 1,
                'day': 2,
            },
        }
    }, {
        'key': 'test_datetime_key',
        'value': {
            'xsi_type': 'DateTimeValue',
            'value': {
                'date': {
                    'year': 2017,
                    'month': 1,
                    'day': 2,
                },
                'hour': 3,
                'minute': 4,
                'second': 5,
                'timeZoneId': 'America/New_York'
            },
        }
    }, {
        'key': 'test_set_key',
        'value': {
            'xsi_type': 'SetValue',
            'values': [
                {'xsi_type': 'NumberValue', 'value': 1},
                {'xsi_type': 'NumberValue', 'value': 2},
            ],
        }
    }]
    target_values.sort(key=lambda v: v['key'])

    statement_result = test_statement.ToStatement()
    self.assertEqual(statement_result['query'],
                     ('WHERE bool_key = :test_bool_key '
                      'AND number_key = :test_number_key '
                      'AND date_key = :test_date_key '
                      'AND datetime_key = :test_datetime_key '
                      'AND set_key = :test_set_key '
                      'LIMIT %s '
                      'OFFSET 0' % googleads.ad_manager.SUGGESTED_PAGE_LIMIT
                     ))

    # The output order doesn't matter, and it's stored internally as a dict
    # until rendered, which is fine, but we need to lock it down for this test.
    self.assertEqual(
        sorted(statement_result['values'], key=lambda v: v['key']),
        target_values
    )

  def testBreakWithSetOfMultipleTypes(self):
    test_statement = googleads.ad_manager.StatementBuilder()
    test_statement.Where('key = :test_key')

    self.assertRaises(
        googleads.errors.GoogleAdsValueError,
        test_statement.WithBindVariable,
        'key', [1, 'a']
    )

  def testMutateVar(self):
    test_statement = googleads.ad_manager.StatementBuilder()
    test_statement.Where('key = :test_key')
    test_statement.WithBindVariable('key', 'abc')
    test_statement.WithBindVariable('key', '123')

    statement_result = test_statement.ToStatement()
    self.assertEqual(len(statement_result['values']), 1)
    self.assertEqual(statement_result['values'][0]['value']['value'], '123')

  def testBreakWithNoTZ(self):
    test_statement = googleads.ad_manager.StatementBuilder()
    test_statement.Where('key = :test_key')

    self.assertRaises(
        googleads.errors.GoogleAdsValueError,
        test_statement.WithBindVariable,
        'key', datetime.datetime.now().replace(tzinfo=None)
    )

  def testBreakWithUnknownType(self):
    test_statement = googleads.ad_manager.StatementBuilder()
    test_statement.Where('key = :test_key')

    class RandomType(object):
      pass

    self.assertRaises(
        googleads.errors.GoogleAdsValueError,
        test_statement.WithBindVariable,
        'key', RandomType()
    )

  def testBreakWithBadSelectFrom(self):
    test_statement = googleads.ad_manager.StatementBuilder()
    test_statement.Select('Id')

    self.assertRaises(googleads.errors.GoogleAdsError,
                      test_statement.ToStatement)

    test_statement.Select(None).From('Line_Item')

    self.assertRaises(googleads.errors.GoogleAdsError,
                      test_statement.ToStatement)


class FilterStatementTest(testing.CleanUtilityRegistryTestCase):
  """Tests for the FilterStatement class."""

  def testFilterStatement(self):
    values = [{
        'key': 'test_key',
        'value': {
            'xsi_type': 'TextValue',
            'value': 'test_value'
        }
    }]
    test_statement = googleads.ad_manager.FilterStatement()
    self.assertEqual(test_statement.ToStatement(),
                     {'query': ' LIMIT 500 OFFSET 0', 'values': None})
    test_statement.offset += 30
    self.assertEqual(test_statement.ToStatement(),
                     {'query': ' LIMIT 500 OFFSET 30', 'values': None})
    test_statement.offset = 123
    test_statement.limit = 5
    self.assertEqual(test_statement.ToStatement(),
                     {'query': ' LIMIT 5 OFFSET 123', 'values': None})
    test_statement = googleads.ad_manager.FilterStatement(
        'SELECT Id FROM Line_Item WHERE key = :test_key', limit=300, offset=20,
        values=values)
    self.assertEqual(test_statement.ToStatement(),
                     {'query': 'SELECT Id FROM Line_Item WHERE key = '
                               ':test_key LIMIT 300 OFFSET 20',
                      'values': values})


if __name__ == '__main__':
  unittest.main()
