#!/usr/bin/python
#
# Copyright 2015 Google Inc. All Rights Reserved.
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

"""This example promotes an experiment.

Promoting an experiment permanently applies all the experimental changes made to
its related ad groups, criteria and ads. To add an experiment, run
add_experiment.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Api: AdWordsOnly
"""


from googleads import adwords


EXPERIMENT_ID = 'INSERT_EXPERIMENT_ID_HERE'


def main(client, experiment_id):
  # Initialize appropriate service.
  experiment_service = client.GetService('ExperimentService', version='v201506')

  # Construct operations and promote experiment.
  operations = [{
      'operator': 'SET',
      'operand': {
          'id': experiment_id,
          'status': 'PROMOTED'
      }
  }]
  result = experiment_service.mutate(operations)

  # Display results.
  for experiment in result['value']:
    print ('Experiment with name \'%s\' and id \'%s\' was promoted.'
           % (experiment['name'], experiment['id']))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, EXPERIMENT_ID)
