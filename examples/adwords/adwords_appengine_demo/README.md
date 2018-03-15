# Python AdWords App Engine Demo

Google's AdWords API lets developers design computer programs that
interact directly with the AdWords platform. With these applications,
advertisers and third parties can more efficiently—and creatively—manage
their large or complex AdWords accounts and campaigns.

App Engine offers a complete development stack that uses familiar technologies
to build and host web applications.

In order for the web application to communicate with AdWords API, we will use
the [Google Ads Python Client Library](https://github.com/googleads/googleads-python-lib).

In this demo, a user signs in and provides their AdWords manager account id and
other credentials that are used to access the AdWords API and provide the
following functionality:

* Retrieve and list client accounts.
* Retrieve and list the Campaigns for a given client account.
* Add new campaigns to a given client account.
* Retrieve and list the AdGroups for a given Campaign.
* Add new AdGroups to a given Campaign.
* Modify the Budget for a given campaign.

SOAP requests can take some time to complete - longer than Google App Engine
will allow. For production-grade web applications, we recommend using the
Task Queue API to handle requests asynchronously. You can read more about this
[here](https://developers.google.com/appengine/docs/python/taskqueue/).


## Step-by-step guide for using AdWords API demo on App Engine:

This guide assumes that you have already set up your AdWords account and have
prepared your OAuth2 Credentials via the Google Developers Console.

1. Install Python v2.7.9 or higher, which you can get
   [here](https://www.python.org/downloads).

1. Install [pip](http://pip.readthedocs.org/en/latest/installing.html),
   if you have not done so already.

1. If you don't have one already,
   [sign up for a Google Account](https://www.google.com/accounts/NewAccount).
   This account will be used to access your AdWords credentials used in making
   API requests.

1. Install the [Google Cloud SDK](https://cloud.google.com/sdk/downloads).

1. Install googleads ands its dependencies locally with the following command,
   executed from this file's parent directory:

   `$ pip install -r requirements.txt -t lib`

1. If you don't already have one, create a new project in the
   [Google Cloud Console](https://console.cloud.google.com). Note the Project
   ID, which you will need in the next step.

1. Configure the Google Cloud SDK with the following steps:

   * While logged into the Google Account you used to create your project, run
     the following command:

     `gcloud auth login`

   * Set your project as the current project with the following command:

     `gcloud config set project ENTER_PROJECT_ID_HERE`

1. You can now deploy this application by running the following command:

    `gcloud app deploy app.yaml -v v1`

1. To view your application in your web browser, run the following command:

   `gcloud app browse`

1. When you go to your App for the first time, you will need to log in and
   provide OAuth2 and AdWords API credentials. You can use credentials
   generated via the generate_refresh_token.py example.

1. With all information entered, you can now use the UI to view and modify
   your account details.


## Where do I submit bug reports and/or feature requests?

Submit bug reports or feature requests to our
[issue tracker](https://github.com/googleads/googleads-python-lib/issues).


## External Dependencies:

* [Python v2.7.9+](https://www.python.org/downloads/)
* [httplib2 v0.9+](https://pypi.python.org/pypi/httplib2)
* [oauth2client v4.0.0+](https://pypi.python.org/pypi/oauth2client/)
* [pysocks v1.5.0+](https://pypi.python.org/pypi/PySocks/)
* [pytz 2014.7+](https://pypi.python.org/pypi/pytz)
* [PyYAML 3.11+](https://pypi.python.org/pypi/PyYAML)
* [suds-jurko 0.6+](https://pypi.python.org/pypi/suds-jurko)
* [xmltodict 0.9.2+](https://pypi.python.org/pypi/xmltodict)
* [App Engine SDK v1.9.11+](https://developers.google.com/appengine/downloads)
* [Google Ads Python Client Library v10.1.0+](https://github.com/googleads/googleads-python-lib)
* [Google Account](https://www.google.com/accounts/NewAccount)
