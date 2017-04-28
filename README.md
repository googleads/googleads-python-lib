#The googleads Python client library


This client library simplifies accessing Google's SOAP Ads APIs - AdWords,
and DoubleClick for Publishers. The library provides easy ways to store your
authentication and create SOAP web service clients. It also contains example
code to help you get started integrating with our APIs.

##Getting started
1. Download and install the library

   *[setuptools](https://pypi.python.org/pypi/setuptools) is a pre-requisite
   for installing the googleads library*

   It is recommended that you install the library and its dependencies from
   PyPI using [pip](https://pip.pypa.io/en/stable/installing/). This can be
   accomplished with a single command:

   `$ pip install googleads`

   As an alternative, you can
   [download the library as a tarball](https://pypi.python.org/pypi/googleads).
   To start the installation, navigate to the directory that contains your
   downloaded unzipped client library and run the "setup.py" script as follows:

   `$ python setup.py build install`

1. Copy the [googleads.yaml](https://github.com/googleads/googleads-python-lib/blob/master/googleads.yaml)
   file to your home directory.

   This will be used to store credentials and other settings that can be loaded
   to initialize a client.

1. Set up your OAuth2 credentials

   The AdWords and DoubleClick for Publishers APIs use
   [OAuth2](http://oauth.net/2/) as the authentication mechanism. Follow the
   appropriate guide below based on your use case.

   **If you're accessing an API using your own credentials...**

   * [Using AdWords](https://github.com/googleads/googleads-python-lib/wiki/API-access-using-own-credentials-(installed-application-flow))
   * [Using DFP](https://github.com/googleads/googleads-python-lib/wiki/API-access-using-own-credentials-(server-to-server-flow))

   **If you're accessing an API on behalf of clients...**

   * [Developing a web application (AdWords or DFP)](https://github.com/googleads/googleads-python-lib/wiki/API-access-on-behalf-of-your-clients-(web-flow))

####Where can I find samples?

You can find code examples for the latest versions of AdWords or DFP on the
[releases](https://github.com/googleads/googleads-python-lib/releases) page.

Alternatively, you can find [AdWords](https://github.com/googleads/googleads-python-lib/tree/master/examples/adwords)
or [DFP](https://github.com/googleads/googleads-python-lib/tree/master/examples/dfp)
samples in the examples directory of this repository.

####Where can I find the pydocs?

Our pydocs can be found [here](http://googleads.github.io/googleads-python-lib).

####Caching authentication information

It is possible to cache your API authentication information. The library
includes a sample file showing how to do this named `googleads.yaml`. Fill
in the fields for the API and features you plan to use. The library's
`LoadFromStorage` methods default to looking for a file with this name in your
home directory, but you can pass in a path to any file with the correct yaml
contents.

```python
# Use the default location - your home directory:
adwords_client = adwords.AdWordsClient.LoadFromStorage()

# Alternatively, pass in the location of the file:
dfp_client = dfp.DfpClient.LoadFromStorage('C:\My\Directory\googleads.yaml')
```

####How do I change the Client Customer Id at runtime?
You can change the Client Customer Id with the following:

```
adwords_client = AdWordsClient.LoadFromStorage()
adwords_client.SetClientCustomerId('my_client_customer_id')
```


##Where do I submit bug reports and/or feature requests?

If you have issues directly related to the client library, use the [issue
tracker](https://github.com/googleads/googleads-python-lib/issues).


If you have issues pertaining to a specific product, use the product support forums:

* [AdWords](https://groups.google.com/forum/#!forum/adwords-api)
* [DoubleClick for Publishers](https://groups.google.com/forum/#!forum/google-doubleclick-for-publishers-api)

Make sure to subscribe to our [Google Plus page](https://plus.google.com/+GoogleAdsDevelopers)
for API change announcements and other news.


##How do I log SOAP interactions?
The library uses Python's built in logging framework. If you wish to log your
SOAP interactions to stdout, you can do the following:
```python
logging.basicConfig(level=logging.INFO, format=googleads.util.LOGGER_FORMAT)
logging.getLogger('suds.transport').setLevel(logging.DEBUG)
```
If you wish to log to a file, you'll need to attach a log handler to this source
which is configured to write the output to a file.


##How do I disable log filters?
By default, this library will apply log filters to the `googleads.common`,
`suds.client`, and `suds.transport` loggers in order to omit sensitive data. If
you need to see this data in your logs, you can disable the filters with the
following:
```python
logging.getLogger('googleads.common').removeFilter(
    googleads.util.GetGoogleAdsCommonFilter())
logging.getLogger('suds.client').removeFilter(
    googleads.util.GetSudsClientFilter())
logging.getLogger('suds.transport').removeFilter(
    googleads.util.GetSudsTransportFilter())
```


##I'm familiar with suds. Can I use suds features with this library?
Yes, you can. The services returned by the `client.GetService()` functions all
have a reference to the underlying suds client stored in the `suds_client`
attribute. You can retrieve the client and use it in familiar ways:
```python
client = AdWordsClient.LoadFromStorage()
campaign_service = client.GetService('CampaignService')
suds_client = campaign_service.suds_client

campaign = suds_client.factory.create('Campaign')
# Set any attributes on the campaign object which you need.
campaign.name = 'My Campaign'
campaign.status = 'PAUSED'

operation = suds_client.factory.create('CampaignOperation')
operation.operator = 'ADD'
operation.operand = campaign

# The service object returned from the client.GetService() call accepts suds
# objects and will set the SOAP and HTTP headers for you.
campaign_service.mutate([operation])

# Alternatively, if you wish to set the headers yourself, you can use the
# suds_client.service directly.
soap_header = suds_client.factory.create('SoapHeader')
soap_header.clientCustomerId = client.client_customer_id
soap_header.developerToken = client.developer_token
soap_header.userAgent = client.user_agent

suds_client.set_options(
    soapheaders=soap_header,
    headers=client.oauth2_client.CreateHttpHeader())

suds_client.service.mutate([operation])
```

##How can I configure or disable caching for the suds client?

By default, the suds clients are cached because reading and digesting the WSDL
can be expensive. However, the default caching method requires permission to
access a local file system that may not be available in certain hosting
environments such as App Engine.

You can pass an implementation of `suds.cache.Cache` to the `AdWordsClient` or
`DfpClient` initializer to modify the default caching behavior.

For example, configuring a different location and duration of the cache file:
```python
doc_cache = suds.cache.DocumentCache(location=cache_path, days=2)
adwords_client = adwords.AdWordsClient(
  developer_token, oauth2_client, user_agent,
  client_customer_id=client_customer_id, cache=doc_cache)
```

You can also disable caching in similar fashion:
```python
adwords_client = adwords.AdWordsClient(
  developer_token, oauth2_client, user_agent,
  client_customer_id=client_customer_id, cache=suds.cache.NoCache())
```

##Timeout Tips
The requests sent by this library are sent via urllib, which is consequently
where the timeout is set. If you set a system timeout elsewhere, the googleads
library will respect it.

You can do the following if you wish to override the timeout:

```python
import socket
socket.setdefaulttimeout(15 * 60)
```

##Requirements

###Python Versions

This library supports both Python 2 and 3. To use this library, you will need to
have Python 2.7.9 (or higher) or Python 3.4 (or higher) installed.

###External Dependencies:

    - httplib2             -- https://pypi.python.org/pypi/httplib2/
    - oauth2client         -- https://pypi.python.org/pypi/oauth2client/
    - suds-jurko           -- https://pypi.python.org/pypi/suds-jurko/
    - pysocks              -- https://pypi.python.org/pypi/PySocks/
    - pytz                 -- https://pypi.python.org/pypi/pytz
    - pyYAML               -- https://pypi.python.org/pypi/pyYAML/
    - xmltodict            -- https://pypi.python.org/pypi/xmltodict/
    - mock                 -- https://pypi.python.org/pypi/mock
                              (only needed to run unit tests)
    - pyfakefs             -- https://pypi.python.org/pypi/pyfakefs
                              (only needed to run unit tests)


##Authors:
    Mark Saniscalchi
