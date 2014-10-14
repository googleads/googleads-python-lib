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

"""Common client library functions and classes used by all products."""

__author__ = 'Joseph DiLallo'

import os
import sys
import warnings

import suds
import yaml

import googleads.errors
import googleads.oauth2

VERSION = '2.1.0'
_COMMON_LIB_SIG = 'googleads/%s' % VERSION
_PYTHON_VERSION = 'Python/%d.%d' % (sys.version_info[0], sys.version_info[1])

# The keys in the authentication dictionary that are used to construct OAuth 2.0
# credentials.
_OAUTH_2_AUTH_KEYS = ('client_id', 'client_secret', 'refresh_token')


def GenerateLibSig(short_name):
  """Generates a library signature suitable for a user agent field.

  Args:
    short_name: The short, product-specific string name for the library.
  Returns:
    A library signature string to append to user-supplied user-agent value.
  """
  return ' (%s, %s, %s)' % (short_name, _COMMON_LIB_SIG, _PYTHON_VERSION)


def LoadFromStorage(path, yaml_key, required_values, optional_values):
  """Loads the data necessary for instantiating a client from file storage.

  In addition to the required_values argument, the yaml file must supply the
  keys used to create OAuth 2.0 credentials.

  Args:
    path: A path string to the yaml document whose keys should be used.
    yaml_key: The key to read in the yaml as a string.
    required_values: A tuple of strings representing values which must be in the
        yaml file. If one of these keys is not in the yaml file, an error will
        be raised.
    optional_values: A tuple of strings representing optional values which may
        be in the yaml file.

  Returns:
    A dictionary map of the keys in the yaml file to their values. This will not
    contain the keys used for OAuth 2.0 client creation and instead will have a
    GoogleOAuth2Client object stored in the 'oauth2_client' field.

  Raises:
    A GoogleAdsValueError if the given yaml file does not contain the
    information necessary to instantiate a client object - either a
    required_values key was missing or an OAuth 2.0 key was missing.
  """
  if not os.path.isabs(path):
    path = os.path.expanduser(path)
  try:
    with open(path, 'r') as handle:
      data = yaml.safe_load(handle.read()).get(yaml_key) or {}
  except IOError:
    raise googleads.errors.GoogleAdsValueError(
        'Given yaml file, %s, could not be opened.' % path)

  original_keys = list(data.keys())
  client_kwargs = {}
  try:
    for key in required_values:
      client_kwargs[key] = data[key]
      del data[key]
  except KeyError:
    raise googleads.errors.GoogleAdsValueError(
        'Your yaml file, %s, is missing some of the required values. Required '
        'values are: %s, actual values are %s'
        % (path, required_values, original_keys))

  try:
    client_kwargs['oauth2_client'] = googleads.oauth2.GoogleRefreshTokenClient(
        data['client_id'], data['client_secret'], data['refresh_token'],
        data.get('https_proxy') or client_kwargs.get('https_proxy'))
    for auth_key in _OAUTH_2_AUTH_KEYS:
      del data[auth_key]
  except KeyError:
    raise googleads.errors.GoogleAdsValueError(
        'Your yaml file, %s, is missing some of the required OAuth 2.0 '
        'values. Required values are: %s, actual values are %s'
        % (path, _OAUTH_2_AUTH_KEYS, original_keys))

  for value in optional_values:
    if value in data:
      client_kwargs[value] = data[value]
      del data[value]

  if data:
    warnings.warn('Your yaml file, %s, contains the following unrecognized '
                  'keys: %s. They were ignored.' % (path, data), stacklevel=3)

  return client_kwargs


def _PackForSuds(obj, factory):
  """Packs SOAP input into the format we want for suds.

  The main goal here is to pack dictionaries with an 'xsi_type' key into
  objects. This allows dictionary syntax to be used even with complex types
  extending other complex types. The contents of dictionaries and lists/tuples
  are recursively packed. Mutable types are copied - we don't mutate the input.

  Args:
    obj: A parameter for a SOAP request which will be packed. If this is
        a dictionary or list, the contents will recursively be packed. If this
        is not a dictionary or list, the contents will be recursively searched
        for instances of unpacked dictionaries or lists.
    factory: The suds.client.Factory object which can create instances of the
        classes generated from the WSDL.

  Returns:
    If the given obj was a dictionary that contained the 'xsi_type' key, this
    will be an instance of a class generated from the WSDL. Otherwise, this will
    be the same data type as the input obj was.
  """
  if obj in ({}, None):
    # Force suds to serialize empty objects. There are legitimate use cases for
    # this, for example passing in an empty SearchCriteria object to a DFA
    # search method in order to select everything.
    return suds.null()
  elif isinstance(obj, dict):
    if 'xsi_type' in obj:
      try:
        new_obj = factory.create(obj['xsi_type'])
      except suds.TypeNotFound:
        new_obj = factory.create(':'.join(['ns0', obj['xsi_type']]))
      # Suds sends an empty XML element for enum types which are not set. None
      # of Google's Ads APIs will accept this. Initializing all of the fields in
      # a suds object to None will ensure that they don't get serialized at all
      # unless the user sets a value. User values explicitly set to None will be
      # packed into a suds.null() object.
      for param, _ in new_obj:
        # Another problem is that the suds.mx.appender.ObjectAppender won't
        # serialize object types with no fields set, but both AdWords and DFP
        # rely on sending objects with just the xsi:type set. The below "if"
        # statement is an ugly hack that gets this to work in all(?) situations
        # by taking advantage of the fact that these classes generally all have
        # a type field. The only other option is to monkey patch ObjectAppender.
        if param.endswith('.Type'):
          setattr(new_obj, param, obj['xsi_type'])
        else:
          setattr(new_obj, param, None)
      for key in obj:
        if key == 'xsi_type': continue
        setattr(new_obj, key, _PackForSuds(obj[key], factory))
    else:
      new_obj = {}
      for key in obj:
        new_obj[key] = _PackForSuds(obj[key], factory)
    return new_obj
  elif isinstance(obj, (list, tuple)):
    return [_PackForSuds(item, factory) for item in obj]
  else:
    _RecurseOverObject(obj, factory)
    return obj


def _RecurseOverObject(obj, factory, parent=None):
  """Recurses over a nested structure to look for changes in Suds objects.

    Args:
      obj: A parameter for a SOAP request field which is to be inspected and
          will be packed for Suds if an xsi_type is specified, otherwise will be
          left unaltered.
      factory: The suds.client.Factory object which can create instances of the
          classes generated from the WSDL.
      parent: The parent object that contains the obj parameter to be inspected.
  """
  if _IsSudsIterable(obj):
    # Since in-place modification of the Suds object is taking place, the
    # iterator should be done over a frozen copy of the unpacked fields.
    copy_of_obj = tuple(obj)
    for item in copy_of_obj:
      if _IsSudsIterable(item):
        if 'xsi_type' in item:
          if isinstance(obj, tuple):
            parent[obj[0]] = _PackForSuds(obj[1], factory)
          else:
            obj.remove(item)
            obj.append(_PackForSuds(item, factory))
        _RecurseOverObject(item, factory, obj)


def _IsSudsIterable(obj):
  """A short helper method to determine if a field is iterable for Suds."""
  return (obj and not isinstance(obj, (basestring, long, int))
          and obj.__iter__)


class SudsServiceProxy(object):
  """Wraps a suds service object, allowing custom logic to be injected.

  This class is responsible for refreshing the HTTP and SOAP headers, so changes
  to the client object will be reflected in future SOAP calls, and for
  transforming SOAP call input parameters, allowing dictionary syntax to be used
  with all SOAP complex types.

  Attributes:
    suds_client: The suds.client.Client this service belongs to. If you are
        familiar with suds and want to use autogenerated classes, you can access
        the client and its factory,
  """

  def __init__(self, suds_client, header_handler):
    """Initializes a suds service proxy.

    Args:
      suds_client: The suds.client.Client whose service will be wrapped. Note
          that this is the client itself, not the client's embedded service
          object.
      header_handler: A HeaderHandler responsible for setting the SOAP and HTTP
          headers on the service client.
    """
    self.suds_client = suds_client
    self._header_handler = header_handler
    self._method_proxies = {}

  def __getattr__(self, attr):
    if attr in self.suds_client.wsdl.services[0].ports[0].methods:
      if attr not in self._method_proxies:
        self._method_proxies[attr] = self._CreateMethod(attr)
      return self._method_proxies[attr]
    else:
      return getattr(self.suds_client.service, attr)

  def _CreateMethod(self, method_name):
    """Create a method wrapping an invocation to the SOAP service.

    Args:
      method_name: A string identifying the name of the SOAP method to call.

    Returns:
      A callable that can be used to make the desired SOAP request.
    """
    soap_service_method = getattr(self.suds_client.service, method_name)

    def MakeSoapRequest(*args):
      """Perform a SOAP call."""
      self._header_handler.SetHeaders(self.suds_client)
      return soap_service_method(*[_PackForSuds(arg, self.suds_client.factory)
                                   for arg in args])

    return MakeSoapRequest


class HeaderHandler(object):
  """A generic header handler interface that must be subclassed by each API."""

  def SetHeaders(self, client):
    """Sets the SOAP and HTTP headers on the given suds client."""
    raise NotImplementedError('You must subclass HeaderHandler.')
