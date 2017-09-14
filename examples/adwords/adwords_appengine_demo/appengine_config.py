# appengine_config.py
import os
from google.appengine.ext import vendor

# Add any libraries install in the "lib" folder.
vendor.add(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'))

