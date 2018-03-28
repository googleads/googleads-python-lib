# Copyright 2016 Google Inc. All Rights Reserved.
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

"""Utilities used by the client library."""

import gzip
import io
import logging
import re
import sys
import threading
import urllib2


from lxml import etree
import suds
import suds.mx
import suds.mx.appender
import zeep


_COMMON_FILTER = None
_SUDS_CLIENT_FILTER = None
_SUDS_MX_CORE_FILTER = None
_SUDS_MX_LITERAL_FILTER = None
_SUDS_TRANSPORT_FILTER = None
LOGGER_FORMAT = '[%(asctime)s - %(name)s - %(levelname)s] %(message)s'


def GetGoogleAdsCommonFilter():
  global _COMMON_FILTER
  if not _COMMON_FILTER:
    _COMMON_FILTER = _GoogleAdsCommonFilter()
  return _COMMON_FILTER


def GetSudsClientFilter():
  global _SUDS_CLIENT_FILTER
  if not _SUDS_CLIENT_FILTER:
    _SUDS_CLIENT_FILTER = _SudsClientFilter()
  return _SUDS_CLIENT_FILTER


def GetSudsMXCoreFilter():
  global _SUDS_MX_CORE_FILTER
  if not _SUDS_MX_CORE_FILTER:
    _SUDS_MX_CORE_FILTER = _SudsMXCoreFilter()
  return _SUDS_MX_CORE_FILTER


def GetSudsMXLiteralFilter():
  global _SUDS_MX_LITERAL_FILTER
  if not _SUDS_MX_LITERAL_FILTER:
    _SUDS_MX_LITERAL_FILTER = _SudsMXLiteralFilter()
  return _SUDS_MX_LITERAL_FILTER


def GetSudsTransportFilter():
  global _SUDS_TRANSPORT_FILTER
  if not _SUDS_TRANSPORT_FILTER:
    _SUDS_TRANSPORT_FILTER = _SudsTransportFilter()
  return _SUDS_TRANSPORT_FILTER


class PatchHelper(object):
  """Utility that applies patches on behalf of the Google Ads Client Library."""

  def Apply(self):
    """Apply patches used by the Google Ads Client Library."""
    self._ApplySudsJurkoAppenderPatch()
    self._ApplySudsJurkoSendPatch()

  def _ApplySudsJurkoAppenderPatch(self):
    """Appends a Monkey Patch to the suds.mx.appender module.

    This resolves an issue where empty objects are ignored and stripped from the
    request output. More details can be found on the suds-jurko issue tracker:
    https://goo.gl/uyYw0C
    """
    def PatchedAppend(self, parent, content):
      obj = content.value
      child = self.node(content)
      parent.append(child)
      for item in obj:
        cont = suds.mx.Content(tag=item[0], value=item[1])
        suds.mx.appender.Appender.append(self, child, cont)

    suds.mx.appender.ObjectAppender.append = PatchedAppend

  def _ApplySudsJurkoSendPatch(self):
    """Appends a Monkey Patch to the suds.transport.http module.

    This allows the suds library to decompress the SOAP body when compression is
    enabled. For more details on SOAP Compression, see:
    https://developers.google.com/adwords/api/docs/guides/bestpractices?hl=en#use_compression
    """
    def GetInflateStream(msg):
      stream = io.BytesIO()
      stream.write(msg)
      stream.flush()
      stream.seek(0)
      return gzip.GzipFile(fileobj=stream, mode='rb')

    def PatchedHttpTransportSend(self, request):
      """Patch for HttpTransport.send to enable gzip compression."""
      msg = request.message
      http_transport = suds.transport.http.HttpTransport
      url = http_transport._HttpTransport__get_request_url(request)
      headers = request.headers
      u2request = urllib2.Request(url, msg, headers)
      self.addcookies(u2request)
      self.proxy = self.options.proxy
      request.headers.update(u2request.headers)
      suds.transport.http.log.debug('sending:\n%s', request)
      try:
        fp = self.u2open(u2request)
      except urllib2.HTTPError, e:
        if e.code in (202, 204):
          return None
        else:
          if e.headers.get('content-encoding') == 'gzip':
            # If gzip encoding is used, decompress here.
            # Need to read and recreate a stream because urllib result objects
            # don't fully implement the file-like API
            e.fp = GetInflateStream(e.fp.read())

          raise suds.transport.TransportError(e.msg, e.code, e.fp)

      self.getcookies(fp, u2request)
      # Note: Python 2 returns httplib.HTTPMessage, and Python 3 returns
      # http.client.HTTPMessage, which differ slightly.
      headers = (fp.headers.dict if sys.version_info < (3, 0) else fp.headers)
      result = suds.transport.Reply(200, headers, fp.read())

      if result.headers.get('content-encoding') == 'gzip':
        # If gzip encoding is used, decompress here.
        result.message = GetInflateStream(result.message).read()

      suds.transport.http.log.debug('received:\n%s', result)
      return result

    suds.transport.http.HttpTransport.send = PatchedHttpTransportSend


class _AbstractDevTokenSOAPFilter(logging.Filter):
  """Interface for sanitizing logs containing SOAP request/response data."""

  _AUTHORIZATION_HEADER = 'authorization'
  _DEVELOPER_TOKEN_SUB = re.compile(
      r'(?<=\<(?:tns|ns0):developerToken\>)'
      r'.*?'
      r'(?=\</(?:tns|ns0):developerToken\>)')
  _REDACTED = 'REDACTED'

  def filter(self, record):
    raise NotImplementedError('You must implement filter().')


class _GoogleAdsCommonFilter(_AbstractDevTokenSOAPFilter):
  """Removes sensitive data from logs generated by googleads.common."""

  def filter(self, record):
    if record.levelno == logging.INFO and record.args:
      content = record.args[0].str()
      content = self._DEVELOPER_TOKEN_SUB.sub(self._REDACTED, content)
      record.args = (content,)
    return True


class _SudsClientFilter(_AbstractDevTokenSOAPFilter):
  """Removes sensitive data from logs generated by suds.client."""
  _SUDS_CLIENT_SOAP_MSG = 'sending to (%s)\nmessage:\n%s'
  _SUDS_CLIENT_HEADERS_MSG = 'headers = %s'

  def filter(self, record):
    args = record.args
    if record.msg == self._SUDS_CLIENT_SOAP_MSG:
      # If the original suds.sax.document.Document is modified, that will also
      # modify the request itself. Instead, replace it with its sanitized text.
      record.args = (args[0], self._DEVELOPER_TOKEN_SUB.sub(
          self._REDACTED, args[1].str()))
    elif record.msg == self._SUDS_CLIENT_HEADERS_MSG:
      sanitized_headers = record.args.copy()
      if self._AUTHORIZATION_HEADER in sanitized_headers:
        sanitized_headers[self._AUTHORIZATION_HEADER] = self._REDACTED
        sanitized_headers.pop(self._AUTHORIZATION_HEADER.capitalize(), None)
      record.args = sanitized_headers
    return True


class _SudsMXCoreFilter(_AbstractDevTokenSOAPFilter):
  """Removes sensitive data from logs generated by suds.mx.core."""

  _DEVELOPER_TOKEN = 'developerToken'
  _REQUEST_HEADER = 'RequestHeader'

  def filter(self, record):
    for i in range(len(record.args)):
      arg = record.args[i]

      if isinstance(arg, suds.mx.Content):
        if arg.tag == self._REQUEST_HEADER:
          # Rather than modifying the argument directly, sets args to a modified
          # copy so that we don't overwrite the headers to be sent in the actual
          # request.
          d = dict(arg.value)
          if self._DEVELOPER_TOKEN in d:
            d[self._DEVELOPER_TOKEN] = self._REDACTED
            record.args = list(record.args)
            record.args[i] = suds.mx.Content(tag=self._REQUEST_HEADER, value=d)
          break
        if arg.tag == self._DEVELOPER_TOKEN:
          # Rather than modifying the argument directly, sets args to a modified
          # copy so that we don't overwrite the headers to be sent in the actual
          # request.
          record.args = list(record.args)
          record.args[i] = suds.mx.Content(
              tag=self._DEVELOPER_TOKEN, value=self._REDACTED)
          break
      elif isinstance(arg, suds.sax.element.Element):
        if arg.name == self._REQUEST_HEADER:
          # Only produce a modified copy of the RequestHeader element if it
          # contains a developer token.
          if arg.getChild(self._DEVELOPER_TOKEN) is not None:
            request_header = suds.sax.element.Element(
                arg.name, parent=arg.parent)

            for child in arg.getChildren():
              copied_child = suds.sax.element.Element(
                  child.name, parent=request_header)

              if child.name == self._DEVELOPER_TOKEN:
                copied_child.text = suds.sax.text.Text(self._REDACTED)
              else:
                copied_child.text = child.text

              request_header.append(copied_child)

            # Rather than modifying the argument directly, sets args to a
            # modified copy so that we don't overwrite the headers to be sent in
            # the actual request.
            record.args = list(record.args)
            record.args[i] = request_header
            break

    return True


class _SudsMXLiteralFilter(_AbstractDevTokenSOAPFilter):
  """Removes sensitive data from logs generated by suds.mx.literal."""

  _DEVELOPER_TOKEN = 'developerToken'
  _REQUEST_HEADER = 'RequestHeader'

  def filter(self, record):
    for i in range(len(record.args)):
      arg = record.args[i]

      if isinstance(arg, suds.mx.Content):
        if arg.tag == self._REQUEST_HEADER:
          # Rather than modifying the argument directly, sets args to a modified
          # copy so that we don't overwrite the headers to be sent in the actual
          # request.
          d = dict(arg.value)
          if self._DEVELOPER_TOKEN in d:
            d[self._DEVELOPER_TOKEN] = self._REDACTED
            record.args = list(record.args)
            record.args[i] = suds.mx.Content(tag=self._REQUEST_HEADER, value=d)
          break
        if arg.tag == self._DEVELOPER_TOKEN:
          # Rather than modifying the argument directly, sets args to a modified
          # copy so that we don't overwrite the headers to be sent in the actual
          # request.
          record.args = list(record.args)
          record.args[i] = suds.mx.Content(tag=self._DEVELOPER_TOKEN,
                                           value=self._REDACTED)
          break

    return True


class _SudsTransportFilter(_AbstractDevTokenSOAPFilter):
  """Removes sensitive data from logs generated by suds.transport."""

  def filter(self, record):
    if record.args:
      arg = record.args[0]
      if isinstance(arg, suds.transport.Request):
        new_arg = suds.transport.Request(arg.url)
        sanitized_headers = arg.headers.copy()
        if self._AUTHORIZATION_HEADER in sanitized_headers:
          sanitized_headers[self._AUTHORIZATION_HEADER] = self._REDACTED
          sanitized_headers.pop(self._AUTHORIZATION_HEADER.capitalize(), None)
        new_arg.headers = sanitized_headers
        new_arg.message = self._DEVELOPER_TOKEN_SUB.sub(
            self._REDACTED, arg.message.decode('utf-8'))
        record.args = (new_arg,)

    return True

_RESPONSE_XML_LOG_LINE = 'Incoming response: \n%s'
_REQUEST_LOG_LINE = 'Request made: Service: "%s" Method: "%s" URL: "%s"'
_REQUEST_XML_LOG_LINE = 'Outgoing request: %s\n%s'
_SOAP_NAMESPACE = 'http://schemas.xmlsoap.org/soap/envelope/'
_FAULT_XPATH = './/{%s}Fault' % _SOAP_NAMESPACE
_HEADER_XPATH = './/{%s}Header' % _SOAP_NAMESPACE
_REMOVE_NS_REGEXP = re.compile(r'^\{.*?\}')


class ZeepLogger(zeep.Plugin, _AbstractDevTokenSOAPFilter):
  """Log zeep request/response data while removing sensitive information."""

  def __init__(self):
    """Instantiates a new ZeepLogger."""
    super(_AbstractDevTokenSOAPFilter, self).__init__()
    self._logger = logging.getLogger('googleads.soap')

  def ingress(self, envelope, http_headers, operation):
    """Overrides the ingress function for response logging.

    Args:
      envelope: An Element with the SOAP request data.
      http_headers: A dict of the current http headers.
      operation: The SoapOperation instance.

    Returns:
      A tuple of the envelope and headers.
    """
    if self._logger.isEnabledFor(logging.DEBUG):
      self._logger.debug(_RESPONSE_XML_LOG_LINE,
                         etree.tostring(envelope, pretty_print=True))

    if self._logger.isEnabledFor(logging.WARN):
      warn_data = {}
      header = envelope.find(_HEADER_XPATH)
      fault = envelope.find(_FAULT_XPATH)
      if fault is not None:
        warn_data['faultMessage'] = fault.find('faultstring').text

        if header is not None:
          header_data = {
              re.sub(_REMOVE_NS_REGEXP, '', child.tag): child.text
              for child in header[0]}
          warn_data.update(header_data)

        if 'serviceName' not in warn_data:
          warn_data['serviceName'] = operation.binding.wsdl.services.keys()[0]

        if 'methodName' not in warn_data:
          warn_data['methodName'] = operation.name

        self._logger.warn('Error summary: %s', warn_data)

    return envelope, http_headers

  def egress(self, envelope, http_headers, operation, binding_options):
    """Overrides the egress function ror request logging.

    Args:
      envelope: An Element with the SOAP request data.
      http_headers: A dict of the current http headers.
      operation: The SoapOperation instance.
      binding_options: An options dict for the SOAP binding.

    Returns:
      A tuple of the envelope and headers.
    """
    if self._logger.isEnabledFor(logging.INFO):
      service_name = operation.binding.wsdl.services.keys()[0]
      self._logger.info(_REQUEST_LOG_LINE, service_name, operation.name,
                        binding_options['address'])

    if self._logger.isEnabledFor(logging.DEBUG):
      http_headers_safe = http_headers.copy()
      if self._AUTHORIZATION_HEADER in http_headers_safe:
        http_headers_safe[self._AUTHORIZATION_HEADER] = self._REDACTED

      request_string = etree.tostring(envelope, pretty_print=True)
      safe_request = self._DEVELOPER_TOKEN_SUB.sub(
          self._REDACTED, request_string.decode('utf-8'))
      self._logger.debug(
          _REQUEST_XML_LOG_LINE, http_headers_safe, safe_request)

    return envelope, http_headers


class UtilityRegistry(object):
  """Utility that registers product utilities used in generating a request."""

  def __contains__(self, utility):
    with self._lock:
      return utility in self._registry

  def __init__(self):
    self._enabled = True
    self._registry = set()
    self._lock = threading.Lock()

  def __iter__(self):
    with self._lock:
      return iter(self._registry.copy())

  def __len__(self):
    with self._lock:
      return len(self._registry)

  def Add(self, obj):
    with self._lock:
      if self._enabled:
        self._registry.add(obj)

  def Clear(self):
    with self._lock:
      self._registry.clear()

  def SetEnabled(self, value):
    with self._lock:
      self._enabled = value
