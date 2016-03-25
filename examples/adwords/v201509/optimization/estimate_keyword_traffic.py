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

"""This example retrieves keyword traffic estimates.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

from googleads import adwords


def main(client):
  # Initialize appropriate service.
  traffic_estimator_service = client.GetService(
      'TrafficEstimatorService', version='v201509')

  # Construct selector object and retrieve traffic estimates.
  keywords = [
      {'text': 'mars cruise', 'matchType': 'BROAD'},
      {'text': 'cheap cruise', 'matchType': 'PHRASE'},
      {'text': 'cruise', 'matchType': 'EXACT'}
  ]
  negative_keywords = [
      {'text': 'moon walk', 'matchType': 'BROAD'}
  ]
  keyword_estimate_requests = []
  for keyword in keywords:
    keyword_estimate_requests.append({
        'keyword': {
            'xsi_type': 'Keyword',
            'matchType': keyword['matchType'],
            'text': keyword['text']
        }
    })

  for keyword in negative_keywords:
    keyword_estimate_requests.append({
        'keyword': {
            'xsi_type': 'Keyword',
            'matchType': keyword['matchType'],
            'text': keyword['text']
        },
        'isNegative': 'true'
    })

  selector = {
      'campaignEstimateRequests': [{
          'adGroupEstimateRequests': [{
              'keywordEstimateRequests': keyword_estimate_requests,
              'maxCpc': {
                  'xsi_type': 'Money',
                  'microAmount': '1000000'
              }
          }],
          'criteria': [
              {
                  'xsi_type': 'Location',
                  'id': '2840'  # United States.
              },
              {
                  'xsi_type': 'Language',
                  'id': '1000'  # English.
              }
          ]
      }]
  }
  estimates = traffic_estimator_service.get(selector)

  # Display results.
  ad_group_estimate = estimates['campaignEstimates'][0]['adGroupEstimates'][0]
  keyword_estimates = ad_group_estimate['keywordEstimates']
  for index in xrange(len(keyword_estimates)):
    keyword = keyword_estimate_requests[index]['keyword']
    estimate = keyword_estimates[index]
    if keyword_estimate_requests[index].get('isNegative', False):
      continue

    # Find the mean of the min and max values.
    mean_avg_cpc = (calc_mean(estimate['min']['averageCpc']['microAmount'],
                              estimate['max']['averageCpc']['microAmount'])
                    if 'averageCpc' in estimate['min'] else 'N/A')
    mean_avg_pos = calc_mean(estimate['min']['averagePosition'],
                             estimate['max']['averagePosition'])
    mean_clicks = calc_mean(estimate['min']['clicksPerDay'],
                            estimate['max']['clicksPerDay'])
    mean_total_cost = calc_mean(estimate['min']['totalCost']['microAmount'],
                                estimate['max']['totalCost']['microAmount'])

    print ('Results for the keyword with text \'%s\' and match type \'%s\':'
           % (keyword['text'], keyword['matchType']))
    print '  Estimated average CPC: %s' % mean_avg_cpc
    print '  Estimated ad position: %s' % mean_avg_pos
    print '  Estimated daily clicks: %s' % mean_clicks
    print '  Estimated daily cost: %s' % mean_total_cost


def fmt_mean(mean):
  if mean:
    return '%.2f' % mean
  else:
    return None


def calc_mean(min_est, max_est):
  if min_est and max_est:
    return (float(min_est) + float(max_est)) / 2.0
  else:
    return None


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client)
