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

"""Unit tests to cover the common module."""

__author__ = 'Joseph DiLallo'

import unittest
import warnings

import fake_filesystem
import fake_tempfile
import mock
import suds
import yaml

import googleads.common
import googleads.errors


class CommonTest(unittest.TestCase):
  """Tests for the googleads.common module."""

  # A dictionary with all the required OAuth 2.0 keys
  _OAUTH_DICT = {'client_id': 'a', 'client_secret': 'b', 'refresh_token': 'c'}

  def setUp(self):
    self.filesystem = fake_filesystem.FakeFilesystem()
    self.tempfile = fake_tempfile.FakeTempfileModule(self.filesystem)
    self.fake_open = fake_filesystem.FakeFileOpen(self.filesystem)

  def _CreateYamlFile(self, key, values, add_oauth=True):
    """Return the filename of a yaml file created for testing."""
    yaml_file = self.tempfile.NamedTemporaryFile(delete=False)
    if add_oauth: values.update(self._OAUTH_DICT)
    with self.fake_open(yaml_file.name, 'w') as yaml_handle:
      yaml_handle.write(yaml.dump({key: values}))
    return yaml_file.name

  def testLoadFromStorage_missingFile(self):
    with mock.patch('googleads.common.open', self.fake_open, create=True):
      self.assertRaises(
          googleads.errors.GoogleAdsValueError,
          googleads.common.LoadFromStorage,
          'yaml_filename', 'woo', [], [])

  def testLoadFromStorage_missingOAuthKey(self):
    yaml_fname = self._CreateYamlFile('woo', {}, False)
    with mock.patch('googleads.common.open', self.fake_open, create=True):
      self.assertRaises(
          googleads.errors.GoogleAdsValueError,
          googleads.common.LoadFromStorage,
          yaml_fname, 'woo', [], [])

  def testLoadFromStorage_passesWithNoRequiredKeys(self):
    yaml_fname = self._CreateYamlFile('woo', {})
    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient') as mock_client:
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        rval = googleads.common.LoadFromStorage(yaml_fname, 'woo', [], [])
        mock_client.assert_called_once_with('a', 'b', 'c', None)
        self.assertEqual({'oauth2_client': mock_client.return_value}, rval)

  def testLoadFromStorage_missingRequiredKey(self):
    with mock.patch('googleads.common.open', self.fake_open, create=True):
      # Both keys are missing.
      yaml_fname = self._CreateYamlFile('two', {})
      self.assertRaises(
          googleads.errors.GoogleAdsValueError,
          googleads.common.LoadFromStorage,
          yaml_fname, 'two', ['needed', 'keys'], [])

      # One key is missing.
      yaml_fname = self._CreateYamlFile('three', {'needed': 'd'})
      self.assertRaises(
          googleads.errors.GoogleAdsValueError,
          googleads.common.LoadFromStorage,
          yaml_fname, 'three', ['needed', 'keys'], [])

  def testLoadFromStorage(self):
    # No optional keys present.
    yaml_fname = self._CreateYamlFile('one', {'needed': 'd', 'keys': 'e',
                                              'https_proxy': 'www.moo.cow'})
    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient') as mock_client:
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        rval = googleads.common.LoadFromStorage(
            yaml_fname, 'one', ['needed', 'keys'], ['other'])
        mock_client.assert_called_once_with('a', 'b', 'c', 'www.moo.cow')
        self.assertEqual({'oauth2_client': mock_client.return_value,
                          'needed': 'd', 'keys': 'e'}, rval)

    # The optional key is present.
    yaml_fname = self._CreateYamlFile('one', {'needed': 'd', 'keys': 'e',
                                              'other': 'f'})
    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient') as mock_client:
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        rval = googleads.common.LoadFromStorage(
            yaml_fname, 'one', ['needed', 'keys'], ['other'])
        mock_client.assert_called_once_with('a', 'b', 'c', None)
        self.assertEqual({'oauth2_client': mock_client.return_value,
                          'needed': 'd', 'keys': 'e', 'other': 'f'}, rval)

  def testLoadFromStorage_relativePath(self):
    fake_os = fake_filesystem.FakeOsModule(self.filesystem)
    yaml_contents = {'one': {'needed': 'd', 'keys': 'e'}}
    yaml_contents['one'].update(self._OAUTH_DICT)
    self.filesystem.CreateFile('/home/test/yaml/googleads.yaml',
                               contents=yaml.dump(yaml_contents))
    fake_os.chdir('/home/test')

    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient') as mock_client:
      with mock.patch('googleads.common.os', fake_os):
        with mock.patch('googleads.common.open', self.fake_open, create=True):
          rval = googleads.common.LoadFromStorage(
              'yaml/googleads.yaml', 'one', ['needed', 'keys'], ['other'])
          mock_client.assert_called_once_with('a', 'b', 'c', None)
          self.assertEqual({'oauth2_client': mock_client.return_value,
                            'needed': 'd', 'keys': 'e'}, rval)

  def testLoadFromStorage_warningWithUnrecognizedKey(self):
    yaml_fname = self._CreateYamlFile('kval', {'Im': 'here', 'whats': 'this?'})
    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient') as mock_client:
      with warnings.catch_warnings(record=True) as captured_warnings:
        with mock.patch('googleads.common.open', self.fake_open, create=True):
          rval = googleads.common.LoadFromStorage(
              yaml_fname, 'kval', ['Im'], ['other'])
          mock_client.assert_called_once_with('a', 'b', 'c', None)
          self.assertEqual({'oauth2_client': mock_client.return_value,
                            'Im': 'here'}, rval)
          self.assertEqual(len(captured_warnings), 1)

  def testGenerateLibSig(self):
    my_name = 'Joseph'
    self.assertEqual(
        ' (%s, %s, %s)' % (my_name, googleads.common._COMMON_LIB_SIG,
                           googleads.common._PYTHON_VERSION),
        googleads.common.GenerateLibSig(my_name))

  def testPackForSuds(self):
    factory = mock.Mock()

    # Test that anything other than list, tuple, and dict pass right through.
    self.assertEqual('input', googleads.common._PackForSuds('input', factory))
    self.assertEqual(set([1]),
                     googleads.common._PackForSuds(set([1]), factory))

    # Test that lists not containing dicts with xsi types return the same
    # values, and test that the input list was not modified.
    input_list = ['1', set([3]), {'moo': 'cow'}]
    self.assertEqual(['1', set([3]), {'moo': 'cow'}],
                     googleads.common._PackForSuds(input_list, factory))
    self.assertEqual(['1', set([3]), {'moo': 'cow'}], input_list)

    # Test that dicts without xsi types return the same values, and test that
    # the input dict was not modified
    input_dict = {'1': 'moo', frozenset([2]): ['val']}
    self.assertEqual({'1': 'moo', frozenset([2]): ['val']},
                     googleads.common._PackForSuds(input_dict, factory))
    self.assertEqual({'1': 'moo', frozenset([2]): ['val']}, input_dict)

    # Now it gets interesting... Test that a dictionary with xsi type gets
    # changed into an object. Test that the input dict is unmodified.
    input_dict = {'xsi_type': 'EliteCampaign', 'name': 'Sales', 'id': 123456,
                  'metadata': {'a': 'b'}}
    factory.create.return_value = mock.MagicMock()
    factory.create.return_value.__iter__.return_value = iter(
        [('id', 0), ('name', 1), ('metadata', 2), ('Campaign.Type', 3),
         ('status', 4)])

    rval = googleads.common._PackForSuds(input_dict, factory)
    factory.create.assert_called_once_with('EliteCampaign')
    self.assertEqual('Sales', rval.name)
    self.assertEqual(123456, rval.id)
    self.assertEqual({'a': 'b'}, rval.metadata)
    self.assertEqual('EliteCampaign', getattr(rval, 'Campaign.Type'))
    self.assertEqual(None, rval.status)
    self.assertEqual({'xsi_type': 'EliteCampaign', 'name': 'Sales',
                      'id': 123456, 'metadata': {'a': 'b'}}, input_dict)

    # Test that this all works recursively. Nest dictionaries in dictionaries in
    # lists in classes.
    factory = mock.Mock()
    factory.create.side_effect = [mock.MagicMock(), mock.MagicMock()]
    input_list = [{'xsi_type': 'EliteCampaign', 'name': 'Sales', 'id': None,
                   'metadata': {'xsi_type': 'metadata', 'a': {'b': 'c'}}},
                  {'i do not have': 'a type'}]
    rval = googleads.common._PackForSuds(input_list, factory)
    factory.create.assert_any_call('EliteCampaign')
    factory.create.assert_any_call('metadata')
    self.assertIsInstance(rval, list)
    self.assertEqual('Sales', rval[0].name)
    self.assertIsInstance(rval[0].id, suds.null)
    self.assertEqual({'b': 'c'}, rval[0].metadata.a)
    self.assertEqual({'i do not have': 'a type'}, rval[1])
    self.assertEqual(
        [{'xsi_type': 'EliteCampaign', 'name': 'Sales', 'id': None,
          'metadata': {'xsi_type': 'metadata', 'a': {'b': 'c'}}},
         {'i do not have': 'a type'}], input_list)

  def testPackForSuds_secondNamespace(self):
    factory = mock.Mock()
    factory.create.side_effect = [suds.TypeNotFound(''), mock.MagicMock()]
    input_list = {'xsi_type': 'EliteCampaign', 'name': 'Sales'}
    rval = googleads.common._PackForSuds(input_list, factory)
    factory.create.assert_any_call('EliteCampaign')
    factory.create.assert_any_call('ns0:EliteCampaign')
    self.assertEqual('Sales', rval.name)


class SudsServiceProxyTest(unittest.TestCase):
  """Tests for the googleads.common.SudsServiceProxy class."""

  def testSudsServiceProxy(self):
    header_handler = mock.Mock()
    port = mock.Mock()
    port.methods = ('SoapMethod',)
    services = mock.Mock()
    services.ports = [port]
    client = mock.Mock()
    client.wsdl.services = [services]
    suds_service_wrapper = googleads.common.SudsServiceProxy(
        client, header_handler)

    self.assertEqual(suds_service_wrapper.SoapMethod,
                     suds_service_wrapper._method_proxies['SoapMethod'])
    self.assertEqual(suds_service_wrapper.NotSoapMethod,
                     client.service.NotSoapMethod)

    with mock.patch('googleads.common._PackForSuds') as mock_pack_for_suds:
      mock_pack_for_suds.return_value = 'modified_test'
      suds_service_wrapper.SoapMethod('test')
      mock_pack_for_suds.assert_called_once_with('test', client.factory)

    client.service.SoapMethod.assert_called_once_with('modified_test')
    header_handler.SetHeaders.assert_called_once_with(client)


class HeaderHandlerTest(unittest.TestCase):
  """Tests for the googleads.common.HeaderHeader class."""

  def testSetHeaders(self):
    """For coverage."""
    self.assertRaises(
        NotImplementedError, googleads.common.HeaderHandler().SetHeaders,
        mock.Mock())


if __name__ == '__main__':
  unittest.main()
