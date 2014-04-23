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

"""Client library for the AdWords API."""

__author__ = 'Joseph DiLallo'

import os
import sys
import urllib
import urllib2
from xml.etree import ElementTree

import suds.client
import suds.mx.literal
import suds.xsd.doctor

import googleads.common
import googleads.errors

# The chunk size used for report downloads.
_CHUNK_SIZE = 16 * 1024
# A giant dictionary of AdWords versions, the services they support, and which
# namespace those services are in.
_SERVICE_MAP = {
    'v201402': {
        'AdGroupAdService': 'cm',
        'AdGroupBidModifierService': 'cm',
        'AdGroupCriterionService': 'cm',
        'AdGroupFeedService': 'cm',
        'AdGroupService': 'cm',
        'AdParamService': 'cm',
        'AdwordsUserListService': 'rm',
        'AlertService': 'mcm',
        'BiddingStrategyService': 'cm',
        'BudgetOrderService': 'billing',
        'BudgetService': 'cm',
        'CampaignAdExtensionService': 'cm',
        'CampaignCriterionService': 'cm',
        'CampaignFeedService': 'cm',
        'CampaignService': 'cm',
        'ConstantDataService': 'cm',
        'ConversionTrackerService': 'cm',
        'CustomerFeedService': 'cm',
        'CustomerService': 'mcm',
        'CustomerSyncService': 'ch',
        'DataService': 'cm',
        'ExperimentService': 'cm',
        'FeedItemService': 'cm',
        'FeedMappingService': 'cm',
        'FeedService': 'cm',
        'GeoLocationService': 'cm',
        'LocationCriterionService': 'cm',
        'ManagedCustomerService': 'mcm',
        'MediaService': 'cm',
        'MutateJobService': 'cm',
        'OfflineConversionFeedService': 'cm',
        'ReportDefinitionService': 'cm',
        'TargetingIdeaService': 'o',
        'TrafficEstimatorService': 'o',
    },
}


class AdWordsClient(object):
  """A central location to set headers and create web service clients.

  Attributes:
    developer_token: A string containing your AdWords API developer token.
    oauth2_client: A googleads.oauth2.GoogleOAuth2Client used to authorize your
        requests.
    user_agent: An arbitrary string which will be used to identify your
        application
    client_customer_id: A string identifying which AdWords customer you want to
        act as.
    validate_only: A boolean indicating if you want your request to be validated
        but not actually executed.
    partial_failure: A boolean indicating if you want your mutate calls
        containing several operations, some of which fail and some of which
        succeed, to result in a complete failure with no changes made or a
        partial failure with some changes made. Only certain services respect
        this header.
    https_proxy: A string identifying the URL of a proxy that all HTTPS requests
        should be routed through. Modifying this value will not affect any SOAP
        service clients you've already created.
  """

  # The key in the storage yaml which contains AdWords data.
  _YAML_KEY = 'adwords'
  # A list of values which must be provided to use AdWords.
  _REQUIRED_INIT_VALUES = ('user_agent', 'developer_token')
  # A list of values which may optionally be provided when using AdWords.
  _OPTIONAL_INIT_VALUES = ('validate_only', 'partial_failure',
                           'client_customer_id', 'https_proxy')
  # The format of SOAP service WSDLs. A server, namespace, version, and service
  # name need to be formatted in.
  _SOAP_SERVICE_FORMAT = '%s/api/adwords/%s/%s/%s?wsdl'

  @classmethod
  def LoadFromStorage(
      cls, path=os.path.join(os.path.expanduser('~'), 'googleads.yaml')):
    """Creates an AdWordsClient with information stored in a yaml file.

    Args:
      [optional]
      path: The path string to the file containing cached AdWords data.

    Returns:
      An AdWordsClient initialized with the values cached in the file.

    Raises:
      A GoogleAdsValueError if the given yaml file does not contain the
      information necessary to instantiate a client object - either a
      required key was missing or an OAuth 2.0 key was missing.
    """
    return cls(**googleads.common.LoadFromStorage(
        path, cls._YAML_KEY, cls._REQUIRED_INIT_VALUES,
        cls._OPTIONAL_INIT_VALUES))

  def __init__(
      self, developer_token, oauth2_client, user_agent,
      client_customer_id=None, validate_only=False, partial_failure=False,
      https_proxy=None):
    """Initializes an AdWordsClient.

    For more information on these arguments, see our SOAP headers guide:
    https://developers.google.com/adwords/api/docs/guides/soap

    Args:
      developer_token: A string containing your AdWords API developer token.
      oauth2_client: A googleads.oauth2.GoogleOAuth2Client used to authorize
          your requests.
      user_agent: An arbitrary string which will be used to identify your
          application
      [optional]
      client_customer_id: A string identifying which AdWords customer you want
          to act as. You do not have to provide this if you are using a client
          account. You probably want to provide this if you're using an MCC
          account.
      validate_only: A boolean indicating if you want your request to be
          validated but not actually executed.
      partial_failure: A boolean indicating if you want your mutate calls
          containing several operations, some of which fail and some of which
          succeed, to result in a complete failure with no changes made or a
          partial failure with some changes made. Only certain services respect
          this header.
      https_proxy: A string identifying the URL of a proxy that all HTTPS
          requests should be routed through.
    """
    self.developer_token = developer_token
    self.oauth2_client = oauth2_client
    self.user_agent = user_agent
    self.client_customer_id = client_customer_id
    self.validate_only = validate_only
    self.partial_failure = partial_failure
    self.https_proxy = https_proxy

  def GetService(self, service_name, version=sorted(_SERVICE_MAP.keys())[-1],
                 server='https://adwords.google.com'):
    """Creates a service client for the given service.

    Args:
      service_name: A string identifying which AdWords service to create a
          service client for.
      [optional]
      version: A string identifying the AdWords version to connect to. This
          defaults to what is currently the latest version. This will be updated
          in future releases to point to what is then the latest version.
      server: A string identifying the webserver hosting the AdWords API.

    Returns:
      A suds.client.ServiceSelector which has the headers and proxy configured
          for use.

    Raises:
      A GoogleAdsValueError if the service or version provided do not exist.
    """
    if server[-1] == '/': server = server[:-1]
    try:
      proxy_option = None
      if self.https_proxy:
        proxy_option = {
            'https': self.https_proxy
        }

      client = suds.client.Client(
          self._SOAP_SERVICE_FORMAT %
          (server, _SERVICE_MAP[version][service_name], version, service_name),
          proxy=proxy_option)
    except KeyError:
      if version in _SERVICE_MAP:
        raise googleads.errors.GoogleAdsValueError(
            'Unrecognized service for the AdWords API. Service given: %s '
            'Supported services: %s'
            % (service_name, _SERVICE_MAP[version].keys()))
      else:
        raise googleads.errors.GoogleAdsValueError(
            'Unrecognized version of the AdWords API. Version given: %s '
            'Supported versions: %s' % (version, _SERVICE_MAP.keys()))

    return googleads.common.SudsServiceProxy(
        client, _AdWordsHeaderHandler(self, version))

  def GetReportDownloader(self, version=sorted(_SERVICE_MAP.keys())[-1],
                          server='https://adwords.google.com'):
    """Creates a downloader for AdWords reports.

    This is a convenience method. It is functionally identical to calling
    ReportDownloader(adwords_client, version, server)

    Args:
      [optional]
      version: A string identifying the AdWords version to connect to. This
          defaults to what is currently the latest version. This will be updated
          in future releases to point to what is then the latest version.
      server: A string identifying the webserver hosting the AdWords API.

    Returns:
      A ReportDownloader tied to this AdWordsClient, ready to download reports.
    """
    return ReportDownloader(self, version, server)


class _AdWordsHeaderHandler(googleads.common.HeaderHandler):
  """Handler which generates the headers for AdWords requests."""

  # The library signature for AdWords, to be appended to all user agents.
  _LIB_SIG = googleads.common.GenerateLibSig('AwApi-Python')
  # The name of the WSDL-defined SOAP Header class used in all SOAP requests.
  # The namespace needs the version of AdWords being used to be templated in.
  _SOAP_HEADER_CLASS = ('{https://adwords.google.com/api/adwords/cm/%s}'
                        'SoapHeader')
  # The content type of report download requests
  _CONTENT_TYPE = 'application/x-www-form-urlencoded'

  def __init__(self, adwords_client, version):
    """Initializes an AdWordsHeaderHandler.

    Args:
      adwords_client: An AdWordsClient whose data will be used to fill in the
          headers. We retain a reference to this object so that the header
          handler picks up changes to the client.
      version: A string identifying which version of AdWords this header handler
          will be used for.
    """
    self._adwords_client = adwords_client
    self._version = version

  def SetHeaders(self, suds_client):
    """Sets the SOAP and HTTP headers on the given suds client."""
    header = suds_client.factory.create(self._SOAP_HEADER_CLASS % self._version)
    header.clientCustomerId = self._adwords_client.client_customer_id
    header.developerToken = self._adwords_client.developer_token
    header.userAgent = ''.join([self._adwords_client.user_agent, self._LIB_SIG])
    header.validateOnly = self._adwords_client.validate_only
    header.partialFailure = self._adwords_client.partial_failure

    suds_client.set_options(
        soapheaders=header,
        headers=self._adwords_client.oauth2_client.CreateHttpHeader())

  def GetReportDownloadHeaders(self, return_money_in_micros=None):
    """Returns a dictionary of headers for a report download request."""
    headers = self._adwords_client.oauth2_client.CreateHttpHeader()
    headers.update({
        'Content-type': self._CONTENT_TYPE,
        'developerToken': str(self._adwords_client.developer_token),
        'clientCustomerId': str(self._adwords_client.client_customer_id),
        'User-Agent': ''.join([self._adwords_client.user_agent, self._LIB_SIG,
                               ',gzip'])
    })
    if return_money_in_micros is not None:
      headers.update({'returnMoneyInMicros': str(return_money_in_micros)})
    return headers


class ReportDownloader(object):
  """A utility that can be used to download reports from AdWords."""

  # The namespace format for report download requests. A version needs to be
  # formatted into it.
  _NAMESPACE_FORMAT = 'https://adwords.google.com/api/adwords/cm/%s'
  # The endpoint format for report download requests. A server and version need
  # to be formatted into it.
  _END_POINT_FORMAT = '%s/api/adwords/reportdownload/%s'
  # The schema location format for report download requests. A server and
  # version need to be formatted into it.
  _SCHEMA_FORMAT = '/'.join([_END_POINT_FORMAT, 'reportDefinition.xsd'])
  # The name of the complex type representing a report definition.
  _REPORT_DEFINITION_NAME = 'reportDefinition'

  def __init__(self, adwords_client, version=sorted(_SERVICE_MAP.keys())[-1],
               server='https://adwords.google.com'):
    """Initializes a ReportDownloader.

    Args:
      adwords_client: The AdwordsClient whose attributes will be used to
          authorize your report download requests.
      [optional]
      version: A string identifying the AdWords version to connect to. This
          defaults to what is currently the latest version. This will be updated
          in future releases to point to what is then the latest version.
      server: A string identifying the webserver hosting the AdWords API.
    """
    if server[-1] == '/': server = server[:-1]
    self._adwords_client = adwords_client
    self._namespace = self._NAMESPACE_FORMAT % version
    self._end_point = self._END_POINT_FORMAT % (server, version)
    self._header_handler = _AdWordsHeaderHandler(adwords_client, version)

    schema_url = self._SCHEMA_FORMAT % (server, version)
    schema = suds.client.Client(
        schema_url,
        doctor=suds.xsd.doctor.ImportDoctor(suds.xsd.doctor.Import(
            self._namespace, schema_url))).wsdl.schema
    self._report_definition_type = schema.elements[
        (self._REPORT_DEFINITION_NAME, self._namespace)]
    self._marshaller = suds.mx.literal.Literal(schema)

  def DownloadReport(self, report_definition, output=sys.stdout,
                     return_money_in_micros=None):
    """Downloads an AdWords report using a report definition.

    The report contents will be written to the given output.

    Args:
      report_definition: A dictionary or instance of the ReportDefinition class
          generated from the schema. This defines the contents of the report
          that will be downloaded.
      [optional]
      output: A writable object where the contents of the report will be written
          to.
      return_money_in_micros: A boolean indicating whether money should be
          represented as micros in reports. If None is supplied the AdWords
          server will use its default value, which is currently True.

    Raises:
      An AdWordsReportBadRequestError if the report download fails due to
      improper input. If the request fails for any other reason (for example,
      a network error), an AdWordsReportError will be raised instead.
    """
    self._DownloadReport(self._SerializeReportDefinition(report_definition),
                         output, return_money_in_micros)

  def DownloadReportWithAwql(self, query, file_format, output=sys.stdout,
                             return_money_in_micros=None):
    """Downloads an AdWords report using an AWQL query.

    The report contents will be written to the given output.

    Args:
      query: A string containing the query which specifies the data you want
          your report to include.
      file_format: A string representing the output format for your report.
          Acceptable values can be found in our API documentation:
          https://developers.google.com/adwords/api/docs/guides/reporting
      [optional]
      output: A writable object where the contents of the report will be written
          to.
      return_money_in_micros: A boolean indicating whether money should be
          represented as micros in reports. If None is supplied the AdWords
          server will use its default value, which is currently True.

    Raises:
      An AdWordsReportBadRequestError if the report download fails due to
      improper input. If the request fails for any other reason (for example,
      a network error), an AdWordsReportError will be raised instead.
    """
    self._DownloadReport(self._SerializeAwql(query, file_format), output,
                         return_money_in_micros)

  def _DownloadReport(self, post_body, output, return_money_in_micros):
    """Downloads an AdWords report, writing the contents to the given file.

    Args:
      post_body: The contents of the POST request's body as a URL encoded
          string.
      output: A writable object where the contents of the report will be written
          to.
      return_money_in_micros: A boolean indicating whether money should be
          represented as micros in reports. If None is supplied the AdWords
          server will use its default value, which is currently True.

    Raises:
      An AdWordsReportBadRequestError if the report download fails due to
      improper input. If the HTTP request fails with any other status code, an
      AdWordsReportError will be raised instead. In the event of certain other
      failures, a urllib2.URLError (Python 2) or urllib.error.URLError
      (Python 3) will be raised.
    """
    if sys.version_info[0] == 3:
      post_body = bytes(post_body, 'utf8')
    request = urllib2.Request(
        self._end_point, post_body,
        self._header_handler.GetReportDownloadHeaders(return_money_in_micros))
    if self._adwords_client.https_proxy:
      request.set_proxy(self._adwords_client.https_proxy, 'https')
    try:
      response = urllib2.urlopen(request)
    except urllib2.HTTPError, e:
      raise self._ExtractError(e)
    else:
      while True:
        chunk = response.read(_CHUNK_SIZE)
        if not chunk: break
        output.write(chunk.decode() if sys.version_info[0] == 3 else chunk)

  def _SerializeAwql(self, query, file_format):
    """Serializes an AWQL query and file format for transport.

    Args:
      query: A string representing the AWQL query used in the report.
      file_format: A string representing the file format of the generated
          report.

    Returns:
      The given query and format URL encoded into the format needed for an
      AdWords report request as a string. This is intended to be a POST body.
    """
    return urllib.urlencode({'__fmt': file_format, '__rdquery': query})

  def _SerializeReportDefinition(self, report_definition):
    """Serializes a report definition for transport.

    Args:
      report_definition: A dictionary or ReportDefinition object to be
          serialized.

    Returns:
      The given report definition serialized into XML and then URL encoded into
      the format needed for an AdWords report request as a string. This is
      intended to be a POST body.
    """
    content = suds.mx.Content(
        tag=self._REPORT_DEFINITION_NAME, value=report_definition,
        name=self._REPORT_DEFINITION_NAME, type=self._report_definition_type)
    return urllib.urlencode({'__rdxml': self._marshaller.process(content)})

  def _ExtractError(self, error):
    """Attempts to extract information from a report download error XML message.

    Args:
      error: A urllib2.HTTPError describing the report download failure.

    Returns:
      An error that should be raised. If the content was an XML error message,
      an AdWordsReportBadRequestError will be returned. Otherwise, an
      AdWordsReportError will be returned.
    """
    content = error.read()
    if sys.version_info[0] == 3:
      content = content.decode()
    if 'reportDownloadError' in content:
      try:
        tree = ElementTree.fromstring(content)
        return googleads.errors.AdWordsReportBadRequestError(
            tree.find('./ApiError/type').text,
            tree.find('./ApiError/trigger').text,
            tree.find('./ApiError/fieldPath').text,
            error.code, error, content)
      except ElementTree.ParseError:
        pass
    return googleads.errors.AdWordsReportError(
        error.code, error, content)
