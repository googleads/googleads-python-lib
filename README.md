#The googleads Python client library


This client library simplifies accessing Google's SOAP Ads APIs - AdWords,
DoubleClick Ad Exchange SOAP, DoubleClick for Advertisers, and DoubleClick for
Publishers. The library provides easy ways to store your authentication and
create SOAP web service clients. It also contains example code to help you get
started integrating with our APIs.

####Important Note Regarding DFP
If you are using v201502 and newer in the DFP API, then performing actions on
objects will fail with an 'args NULL' error due to a bug in the underlying SOAP
client, more details here: https://github.com/googleads/googleads-python-lib/issues/58.

While the fix has been accepted and merged into the source, you will need to download
the source files yourself and install them directly. The source can be located here:
https://bitbucket.org/jurko/suds/downloads

##How do I get started?
####Installing the library
Install or update the library from PyPI. If you're using pip, this is as easy
as:

`$ pip install [--upgrade] googleads`

If you don't want to install directly from PyPI, you can download the library
as a tarball and then install it manually. The download can be found here:
https://pypi.python.org/pypi/googleads
Navigate to the directory that contains your downloaded unzipped client
library and run the "setup.py" script to install the "googleads"
module.

`$ python setup.py build install`

You can find code examples in the git repo and in the library's releases within
the examples folder.

####Where can I find the pydocs?
Our pydocs are hosted at: http://googleads.github.io/googleads-python-lib

####Caching authentication information
It is possible to cache your API authentication information. The library
includes a sample file showing how to do this named `googleads.yaml`. Fill
in the fields for the API you plan to use. The library's `LoadFromStorage`
methods default to looking for a file with this name in your home directory,
but you can pass in a path to any file with the correct yaml contents.

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
* [DoubleClick Ad Exchange](https://groups.google.com/forum/#!forum/google-doubleclick-ad-exchange-buyer-api)
* [DoubleClick for Advertisers](https://groups.google.com/forum/#!forum/google-doubleclick-for-advertisers-api)
* [DoubleClick for Publishers](https://groups.google.com/forum/#!forum/google-doubleclick-for-publishers-api)

Make sure to subscribe to our [Google Plus page](https://plus.google.com/+GoogleAdsDevelopers)
for API change announcements and other news.


##How do I log SOAP interactions?
The library uses Python's built in logging framework. If you wish to log your
SOAP interactions to stdout, you can do the following:
```python
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.transport').setLevel(logging.DEBUG)
```
If you wish to log to a file, you'll need to attach a log handler to this source
which is configured to write the output to a file.


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


##External Dependencies:


    - oauthlib             -- http://pypi.python.org/pypi/oauthlib/
    - suds-jurko           -- http://pypi.python.org/pypi/suds-jurko/
    - pytz                 -- https://pypi.python.org/pypi/pytz
    - pyYAML               -- http://pypi.python.org/pypi/pyYAML/
    - mock                 -- http://pypi.python.org/pypi/mock
                              (only needed to run unit tests)
    - pyfakefs             -- https://pypi.python.org/pypi/pyfakefs
                              (only needed to run unit tests)


##Running The Test Suite

You can run test modules one by one:

    $ cd tests
    $ ./adwords_test.py
    ...

To make things simpler, you can also use `nose` for test discovery:

    $ pip install nose
    $ nosetests tests/*.py


##Authors:
    Mark Saniscalchi
