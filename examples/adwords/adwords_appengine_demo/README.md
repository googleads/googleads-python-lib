# Python AdWords App Engine Demo

Google's AdWords API lets developers design computer programs that
interact directly with the AdWords platform. With these applications,
advertisers and third parties can more efficiently—and creatively—manage
their large or complex AdWords accounts and campaigns.

App Engine offers a complete development stack that uses familiar technologies
to build and host web applications.

In order for the web application to communicate with AdWords API, we will use
the [Google Ads Python Client Library](https://github.com/googleads/googleads-python-lib).

In this demo, a user signs in and provides their MCC Client Customer Id and
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

1. Install Python v2.7, which you can get
   [here](https://www.python.org/downloads).

2. Install [pip](http://pip.readthedocs.org/en/latest/installing.html),
   if you have not done so already.

3. If you don't have one already,
   [sign up for a Google Account](https://www.google.com/accounts/NewAccount).
   This account will be used to access your AdWords credentials used in making
   API requests.

4. Download the latest version of the
   [App Engine SDK](https://developers.google.com/appengine/downloads) and
   unpack its content. This demo should be compatible with  v1.9.11+.

5. Install googleads with the following command:

   `$ pip install googleads`

   Then copy the googleads package from your Python installation's
   dist-packages directory into this project. The installation of googleads
   should also have installed the dependencies referred to in the following
   steps.

6. Copy the httplib2 package from your Python installation's dist-packages
   directory into this project.

7. Copy the oauth2client package from your Python installation's dist-packages
   directory into this project.

8. Copy the pytz package from your Python installation's dist-packages
   directory into this project.

9. Copy socks.py from the PySocks tarball found in your Python installation's
   dist-packages directory into this project.

10. Copy the suds package from your Python installation's dist-packages
   directory into this project.

11. Create an App Engine application in the
   [Google App Engine Console](https://appengine.google.com/).

12. Go to this project's app.yaml, and enter in your application name for the
   "application" field.

13. You can now deploy this project by running the following command:

    `python $APPENGINE_SDK_DIR/appcfg --oauth2 update .`

14. When you go to your App for the first time, you will need to log in and
    provide OAuth2 and AdWords API credentials. You can use credentials
    generated via the generate_refresh_token.py example.

15. With all information entered, you can now use the UI to view and modify
    your account details.


## Where do I submit bug reports and/or feature requests?

Submit bug reports or feature requests to our
[issue tracker](https://github.com/googleads/googleads-python-lib/issues).


## External Dependencies:

* [Python v2.7](https://www.python.org/downloads/)
* [httplib2 v0.9+](https://pypi.python.org/pypi/httplib2)
* [oauth2client v1.4.5+](https://pypi.python.org/pypi/oauth2client/)
* [pysocks v1.5.0+](https://pypi.python.org/pypi/PySocks/)
* [pytz 2014.7+](https://pypi.python.org/pypi/pytz)
* [suds-jurko 0.6+](https://pypi.python.org/pypi/suds-jurko)
* [App Engine SDK v1.9.11+](https://developers.google.com/appengine/downloads)
* [Google Ads Python Client Library v2.1.0+](https://github.com/googleads/googleads-python-lib)
* [Google Account](https://www.google.com/accounts/NewAccount)


### Author:

api.msaniscalchi@gmail.com (Mark Saniscalchi)