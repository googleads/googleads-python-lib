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

"""Client library for the DoubleClick for Publishers API."""


import csv
import datetime
import logging
import os
import time
import urllib2

import pytz
import suds.client
import suds.transport

import googleads.common
import googleads.errors

# The default application name.
DEFAULT_APPLICATION_NAME = 'INSERT_APPLICATION_NAME_HERE'
# The endpoint server for DFP.
DEFAULT_ENDPOINT = 'https://ads.google.com'
# The suggested page limit per page fetched from the API.
SUGGESTED_PAGE_LIMIT = 500
# The chunk size used for report downloads.
_CHUNK_SIZE = 16 * 1024
# A giant dictionary of DFP versions and the services they support.
_SERVICE_MAP = {
    'v201502':
        ('ActivityGroupService', 'ActivityService', 'AdExclusionRuleService',
         'AdRuleService', 'AudienceSegmentService', 'BaseRateService',
         'CompanyService', 'ContactService', 'ContentBundleService',
         'ContentMetadataKeyHierarchyService', 'ContentService',
         'CreativeService', 'CreativeSetService', 'CreativeTemplateService',
         'CreativeWrapperService', 'CustomFieldService',
         'CustomTargetingService', 'ExchangeRateService', 'ForecastService',
         'InventoryService', 'LabelService',
         'LineItemCreativeAssociationService', 'LineItemService',
         'LineItemTemplateService', 'LiveStreamEventService', 'NetworkService',
         'OrderService', 'PackageService', 'PlacementService',
         'PremiumRateService', 'ProductService', 'ProductPackageService',
         'ProductPackageItemService', 'ProductTemplateService',
         'ProposalLineItemService', 'ProposalService',
         'PublisherQueryLanguageService', 'RateCardService',
         'ReconciliationOrderReportService', 'ReconciliationReportRowService',
         'ReconciliationReportService', 'ReportService', 'SharedAdUnitService',
         'SuggestedAdUnitService', 'TeamService', 'UserService',
         'UserTeamAssociationService', 'WorkflowRequestService'),
    'v201505':
        ('ActivityGroupService', 'ActivityService', 'AdExclusionRuleService',
         'AdRuleService', 'AudienceSegmentService', 'BaseRateService',
         'CompanyService', 'ContactService', 'ContentBundleService',
         'ContentMetadataKeyHierarchyService', 'ContentService',
         'CreativeService', 'CreativeSetService', 'CreativeTemplateService',
         'CreativeWrapperService', 'CustomFieldService',
         'CustomTargetingService', 'ExchangeRateService', 'ForecastService',
         'InventoryService', 'LabelService',
         'LineItemCreativeAssociationService', 'LineItemService',
         'LineItemTemplateService', 'LiveStreamEventService', 'NetworkService',
         'OrderService', 'PackageService', 'PlacementService',
         'PremiumRateService', 'ProductService', 'ProductPackageService',
         'ProductPackageItemService', 'ProductTemplateService',
         'ProposalLineItemService', 'ProposalService',
         'PublisherQueryLanguageService', 'RateCardService',
         'ReconciliationOrderReportService', 'ReconciliationReportRowService',
         'ReconciliationReportService', 'ReportService', 'SharedAdUnitService',
         'SuggestedAdUnitService', 'TeamService', 'UserService',
         'UserTeamAssociationService', 'WorkflowRequestService'),
    'v201508':
        ('ActivityGroupService', 'ActivityService', 'AdExclusionRuleService',
         'AdRuleService', 'AudienceSegmentService', 'BaseRateService',
         'CompanyService', 'ContactService', 'ContentBundleService',
         'ContentMetadataKeyHierarchyService', 'ContentService',
         'CreativeService', 'CreativeSetService', 'CreativeTemplateService',
         'CreativeWrapperService', 'CustomFieldService',
         'CustomTargetingService', 'ExchangeRateService', 'ForecastService',
         'InventoryService', 'LabelService',
         'LineItemCreativeAssociationService', 'LineItemService',
         'LineItemTemplateService', 'LiveStreamEventService', 'NetworkService',
         'OrderService', 'PackageService', 'PlacementService',
         'PremiumRateService', 'ProductService', 'ProductPackageService',
         'ProductPackageItemService', 'ProductTemplateService',
         'ProposalLineItemService', 'ProposalService',
         'PublisherQueryLanguageService', 'RateCardService',
         'ReconciliationOrderReportService', 'ReconciliationReportRowService',
         'ReconciliationLineItemReportService',
         'ReconciliationReportService', 'ReportService', 'SharedAdUnitService',
         'SuggestedAdUnitService', 'TeamService', 'UserService',
         'UserTeamAssociationService', 'WorkflowRequestService'),
    'v201511':
        ('ActivityGroupService', 'ActivityService', 'AdExclusionRuleService',
         'AdRuleService', 'AudienceSegmentService', 'BaseRateService',
         'CompanyService', 'ContactService', 'ContentBundleService',
         'ContentMetadataKeyHierarchyService', 'ContentService',
         'CreativeService', 'CreativeSetService', 'CreativeTemplateService',
         'CreativeWrapperService', 'CustomFieldService',
         'CustomTargetingService', 'ExchangeRateService', 'ForecastService',
         'InventoryService', 'LabelService',
         'LineItemCreativeAssociationService', 'LineItemService',
         'LineItemTemplateService', 'LiveStreamEventService', 'NetworkService',
         'OrderService', 'PackageService', 'PlacementService',
         'PremiumRateService', 'ProductService', 'ProductPackageService',
         'ProductPackageItemService', 'ProductTemplateService',
         'ProposalLineItemService', 'ProposalService',
         'PublisherQueryLanguageService', 'RateCardService',
         'ReconciliationOrderReportService', 'ReconciliationReportRowService',
         'ReconciliationLineItemReportService',
         'ReconciliationReportService', 'ReportService', 'SharedAdUnitService',
         'SuggestedAdUnitService', 'TeamService', 'UserService',
         'UserTeamAssociationService', 'WorkflowRequestService'),
    'v201602':
        ('ActivityGroupService', 'ActivityService', 'AdExclusionRuleService',
         'AdRuleService', 'AudienceSegmentService', 'BaseRateService',
         'CompanyService', 'ContactService', 'ContentBundleService',
         'ContentMetadataKeyHierarchyService', 'ContentService',
         'CreativeService', 'CreativeSetService', 'CreativeTemplateService',
         'CreativeWrapperService', 'CustomFieldService',
         'CustomTargetingService', 'ExchangeRateService', 'ForecastService',
         'InventoryService', 'LabelService',
         'LineItemCreativeAssociationService', 'LineItemService',
         'LineItemTemplateService', 'LiveStreamEventService', 'NetworkService',
         'OrderService', 'PackageService', 'PlacementService',
         'PremiumRateService', 'ProductService', 'ProductPackageService',
         'ProductPackageItemService', 'ProductTemplateService',
         'ProposalLineItemService', 'ProposalService',
         'PublisherQueryLanguageService', 'RateCardService',
         'ReconciliationOrderReportService', 'ReconciliationReportRowService',
         'ReconciliationLineItemReportService',
         'ReconciliationReportService', 'ReportService',
         'SuggestedAdUnitService', 'TeamService', 'UserService',
         'UserTeamAssociationService', 'WorkflowRequestService'),
}


class DfpClient(object):
  """A central location to set headers and create web service clients.

  Attributes:
    oauth2_client: A googleads.oauth2.GoogleOAuth2Client used to authorize your
        requests.
    application_name: An arbitrary string which will be used to identify your
        application
    network_code: A string identifying the network code of the network you are
        accessing. All requests other than some NetworkService calls require
        this header to be set.
    https_proxy: A string identifying the URL of a proxy that all HTTPS requests
        should be routed through. Modifying this value will not affect any SOAP
        service clients you've already created.
  """

  # The key in the storage yaml which contains DFP data.
  _YAML_KEY = 'dfp'
  # A list of values which must be provided to use DFP.
  _REQUIRED_INIT_VALUES = ('application_name',)
  # A list of values which may optionally be provided when using DFP.
  _OPTIONAL_INIT_VALUES = (
      'network_code', 'https_proxy')
  # The format of SOAP service WSDLs. A server, version, and service name need
  # to be formatted in.
  _SOAP_SERVICE_FORMAT = '%s/apis/ads/publisher/%s/%s?wsdl'

  @classmethod
  def LoadFromStorage(cls, path=None):
    """Creates a DfpClient with information stored in a yaml file.

    Args:
      [optional]
      path: str The path to the file containing cached DFP data.

    Returns:
      A DfpClient initialized with the values cached in the file.

    Raises:
      A GoogleAdsValueError if the given yaml file does not contain the
      information necessary to instantiate a client object - either a
      required key was missing or an OAuth 2.0 key was missing.
    """
    if path is None:
      path = os.path.join(os.path.expanduser('~'), 'googleads.yaml')

    return cls(**googleads.common.LoadFromStorage(
        path, cls._YAML_KEY, cls._REQUIRED_INIT_VALUES,
        cls._OPTIONAL_INIT_VALUES))

  def __init__(self, oauth2_client, application_name, network_code=None,
               https_proxy=None, cache=None):
    """Initializes a DfpClient.

    For more information on these arguments, see our SOAP headers guide:
    https://developers.google.com/doubleclick-publishers/docs/soap_xml

    Args:
      oauth2_client: A googleads.oauth2.GoogleOAuth2Client used to authorize
          your requests.
      application_name: An arbitrary string which will be used to identify your
          application
      [optional]
      network_code: A string identifying the network code of the network you are
          accessing. All requests other than getAllNetworks and getCurrentUser
          calls require this header to be set.
      https_proxy: A string identifying the proxy that all HTTPS requests
          should be routed through.
      cache: A subclass of suds.cache.Cache; defaults to None.
    """
    if application_name is DEFAULT_APPLICATION_NAME:
      raise googleads.errors.GoogleAdsValueError(
          'Application name must be set and not be the default [%s]' %
          DEFAULT_APPLICATION_NAME)

    self.oauth2_client = oauth2_client
    self.application_name = application_name
    self.network_code = network_code
    self.https_proxy = https_proxy
    self.cache = cache
    self._header_handler = _DfpHeaderHandler(self)

  def GetService(self, service_name, version=sorted(_SERVICE_MAP.keys())[-1],
                 server=DEFAULT_ENDPOINT):
    """Creates a service client for the given service.

    Args:
      service_name: A string identifying which DFP service to create a service
          client for.
      [optional]
      version: A string identifying the DFP version to connect to. This defaults
          to what is currently the latest version. This will be updated in
          future releases to point to what is then the latest version.
      server: A string identifying the webserver hosting the DFP API.

    Returns:
      A suds.client.ServiceSelector which has the headers and proxy configured
          for use.

    Raises:
      A GoogleAdsValueError if the service or version provided do not exist.
    """
    server = server[:-1] if server[-1] == '/' else server
    try:
      proxy_option = None
      if self.https_proxy:
        proxy_option = {
            'https': self.https_proxy
        }

      client = suds.client.Client(
          self._SOAP_SERVICE_FORMAT % (server, version, service_name),
          proxy=proxy_option, cache=self.cache, timeout=3600)
    except suds.transport.TransportError:
      if version in _SERVICE_MAP:
        if service_name in _SERVICE_MAP[version]:
          raise
        else:
          raise googleads.errors.GoogleAdsValueError(
              'Unrecognized service for the DFP API. Service given: %s '
              'Supported services: %s'
              % (service_name, _SERVICE_MAP[version]))
      else:
        raise googleads.errors.GoogleAdsValueError(
            'Unrecognized version of the DFP API. Version given: %s Supported '
            'versions: %s' % (version, _SERVICE_MAP.keys()))

    return googleads.common.SudsServiceProxy(client, self._header_handler)

  def GetDataDownloader(self, version=sorted(_SERVICE_MAP.keys())[-1],
                        server=DEFAULT_ENDPOINT):
    """Creates a downloader for DFP reports and PQL result sets.

    This is a convenience method. It is functionally identical to calling
    DataDownloader(dfp_client, version, server)

    Args:
      [optional]
      version: A string identifying the DFP version to connect to. This defaults
          to what is currently the latest version. This will be updated in
          future releases to point to what is then the latest version.
      server: A string identifying the webserver hosting the DFP API.

    Returns:
      A DataDownloader tied to this DfpClient, ready to download reports.
    """
    return DataDownloader(self, version, server)


class _DfpHeaderHandler(googleads.common.HeaderHandler):
  """Handler which sets the headers for a DFP SOAP call."""

  # The library signature for DFP, to be appended to all application_names.
  _LIB_SIG = googleads.common.GenerateLibSig('DfpApi-Python')
  # The name of the WSDL-defined SOAP Header class used in all requests.
  _SOAP_HEADER_CLASS = 'SoapRequestHeader'

  def __init__(self, dfp_client):
    """Initializes a DfpHeaderHandler.

    Args:
      dfp_client: The DfpClient whose data will be used to fill in the headers.
          We retain a reference to this object so that the header handler picks
          up changes to the client.
    """
    self._dfp_client = dfp_client

  def SetHeaders(self, suds_client):
    """Sets the SOAP and HTTP headers on the given suds client."""
    header = suds_client.factory.create(self._SOAP_HEADER_CLASS)
    header.networkCode = self._dfp_client.network_code
    header.applicationName = ''.join([self._dfp_client.application_name,
                                      self._LIB_SIG])

    suds_client.set_options(
        soapheaders=header,
        headers=self._dfp_client.oauth2_client.CreateHttpHeader())


class FilterStatement(object):
  """A statement object for PQL and get*ByStatement queries.

  The FilterStatement object allows for user control of limit/offset. It
  automatically limits queries to the suggested page limit if not explicitly
  set.
  """

  def __init__(
      self, where_clause='', values=None, limit=SUGGESTED_PAGE_LIMIT, offset=0):
    self.where_clause = where_clause
    self.values = values
    self.limit = limit
    self.offset = offset

  def ToStatement(self):
    """Returns this statement object in the format DFP requires."""
    return {'query': ('%s LIMIT %d OFFSET %d' %
                      (self.where_clause, self.limit, self.offset)),
            'values': self.values}


class DataDownloader(object):
  """A utility that can be used to download reports and PQL result sets."""

  def __init__(self, dfp_client, version=sorted(_SERVICE_MAP.keys())[-1],
               server=DEFAULT_ENDPOINT):
    """Initializes a DataDownloader.

    Args:
      dfp_client: The DfpClient whose attributes will be used to authorize your
          report download and PQL query requests.
      [optional]
      version: A string identifying the DFP version to connect to. This defaults
          to what is currently the latest version. This will be updated in
          future releases to point to what is then the latest version.
      server: A string identifying the webserver hosting the DFP API.
    """
    if server[-1] == '/': server = server[:-1]
    self._dfp_client = dfp_client
    self._version = version
    self._server = server
    self._report_service = None
    self._pql_service = None

  def _GetReportService(self):
    """Lazily initializes a report service client."""
    if not self._report_service:
      self._report_service = self._dfp_client.GetService(
          'ReportService', self._version, self._server)
    return self._report_service

  def _GetPqlService(self):
    """Lazily initializes a PQL service client."""
    if not self._pql_service:
      self._pql_service = self._dfp_client.GetService(
          'PublisherQueryLanguageService', self._version, self._server)
    return self._pql_service

  def WaitForReport(self, report_job):
    """Runs a report, then waits (blocks) for the report to finish generating.

    Args:
      report_job: The report job to wait for. This may be a dictionary or an
          instance of the suds-generated ReportJob class.

    Returns:
      The completed report job's ID as a string.

    Raises:
      A DfpReportError if the report job fails to complete.
    """
    service = self._GetReportService()
    report_job_id = service.runReportJob(report_job)['id']

    if self._version > 'v201502':
      status = service.getReportJobStatus(report_job_id)
    else:
      status = service.getReportJob(report_job_id)['reportJobStatus']

    while status != 'COMPLETED' and status != 'FAILED':
      logging.debug('Report job status: %s', status)
      time.sleep(30)
      if self._version > 'v201502':
        status = service.getReportJobStatus(report_job_id)
      else:
        status = service.getReportJob(report_job_id)['reportJobStatus']

    if status == 'FAILED':
      raise googleads.errors.DfpReportError(report_job_id)
    else:
      logging.debug('Report has completed successfully')
      return report_job_id

  def DownloadReportToFile(self, report_job_id, export_format, outfile):
    """Downloads report data and writes it to a file.

    The report job must be completed before calling this function.

    Args:
      report_job_id: The ID of the report job to wait for, as a string.
      export_format: The export format for the report file, as a string.
      outfile: A writeable, file-like object to write to.
    """
    service = self._GetReportService()
    report_url = service.getReportDownloadURL(report_job_id, export_format)
    response = urllib2.urlopen(report_url)
    while True:
      chunk = response.read(_CHUNK_SIZE)
      if not chunk: break
      outfile.write(chunk)

  def DownloadPqlResultToList(self, pql_query, values=None):
    """Downloads the results of a PQL query to a list.

    Args:
      pql_query: str a statement filter to apply (the query should not include
                 the limit or the offset)
      [optional]
      values: list dict of bind values to use with the pql_query.

    Returns:
      a list of lists with the first being the header row and each subsequent
      list being a row of results.
    """
    results = []
    self._PageThroughPqlSet(pql_query, results.append, values)
    return results

  def DownloadPqlResultToCsv(self, pql_query, file_handle, values=None):
    """Downloads the results of a PQL query to CSV.

    Args:
      pql_query: str a statement filter to apply (the query should not include
                 the limit or the offset)
      file_handle: file the file object to write to.
      [optional]
      values: list dict of bind values to use with the pql_query.
    """
    pql_writer = csv.writer(file_handle, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
    self._PageThroughPqlSet(pql_query, pql_writer.writerow, values)

  def _ConvertValueForCsv(self, pql_value):
    """Sanitizes a field value from a Value object to a CSV suitable format.

    Args:
      pql_value: dict a dictionary containing the data for a single field of an
                 entity.

    Returns:
      str a CSV writer friendly value formatted by Value.Type.
    """
    if 'value' in pql_value:
      field = pql_value['value']
    elif 'values' in pql_value:
      field = pql_value['values']
    else:
      field = None

    if field:
      if isinstance(field, list):
        if all(DfpClassType(single_field) == DfpClassType(field[0])
               for single_field in field):
          return ','.join([
              '"%s"' % str(self._ConvertValueForCsv(single_field))
              for single_field in field])
        else:
          raise googleads.errors.GoogleAdsValueError(
              'The set value returned contains unsupported mix value types')

      class_type = DfpClassType(pql_value)

      if class_type == 'TextValue':
        return field.replace('"', '""').encode('UTF8')
      elif class_type == 'NumberValue':
        return float(field) if '.' in field else int(field)
      elif class_type == 'DateTimeValue':
        return self._ConvertDateTimeToOffset(field)
      elif class_type == 'DateValue':
        return datetime.date(int(field['date']['year']),
                             int(field['date']['month']),
                             int(field['date']['day'])).isoformat()
      else:
        return field
    else:
      return '-'

  def _PageThroughPqlSet(self, pql_query, output_function, values):
    """Pages through a pql_query and performs an action (output_function).

    Args:
      pql_query: str a statement filter to apply (the query should not include
                 the limit or the offset)
      output_function: the function to call to output the results (csv or in
                       memory)
      values: list dict of bind values to use with the pql_query.
    """
    result_set_size = 0
    pql_service = self._GetPqlService()
    filter_statement = FilterStatement(pql_query, values, SUGGESTED_PAGE_LIMIT)

    while True:
      response = pql_service.select(filter_statement.ToStatement())

      if 'rows' in response:
        # Write the header row only on first pull
        if filter_statement.offset == 0:
          header = response['columnTypes']
          output_function([label['labelName'] for label in header])

        entities = response['rows']
        result_set_size = len(entities)

        for entity in entities:
          output_function([self._ConvertValueForCsv(value) for value
                           in entity['values']])

        filter_statement.offset += result_set_size
        if result_set_size != SUGGESTED_PAGE_LIMIT:
          break
      else:
        break

  def _ConvertDateTimeToOffset(self, date_time_value):
    """Converts the PQL formatted response for a dateTime object.

    Output conforms to ISO 8061 format, e.g. 'YYYY-MM-DDTHH:MM:SSz.'

    Args:
      date_time_value: dict The date time value from the PQL response.

    Returns:
      str: A string representation of the date time value uniform to
           ReportService.
    """
    date_time_obj = datetime.datetime(int(date_time_value['date']['year']),
                                      int(date_time_value['date']['month']),
                                      int(date_time_value['date']['day']),
                                      int(date_time_value['hour']),
                                      int(date_time_value['minute']),
                                      int(date_time_value['second']))
    date_time_str = pytz.timezone(
        date_time_value['timeZoneID']).localize(date_time_obj).isoformat()

    if date_time_str[-5:] == '00:00':
      return date_time_str[:-6] + 'Z'
    else:
      return date_time_str


def DfpClassType(value):
  """Returns the class type for the Suds object.

  Args:
    value: generic Suds object to return type for.

  Returns:
    str: A string representation of the value response type.
  """
  return value.__class__.__name__
