"""
A simple example using the Python SDK to count how many buckets are on the Igneous system.

This example program assumes that IGNEOUS_API_SERVER and IGNEOUS_API_KEY are set in the environment.
"""
import os
import igneous

client = igneous.Client(api_server=os.environ['IGNEOUS_API_SERVER'], api_key=os.environ['IGNEOUS_API_KEY'])
response: dict = client.buckets_list()

"""
A successful response will always have this structure:

{
    'ok': True,
    'reason': 'OK',
    'code': 200,
    'request': {
        'url': '<SERVER URL THAT WAS ACTUALLY HIT>' ,
        'method': 'get',
        'headers': {
            'Authorization': '<THE CONTENT OF IGNEOUS_API_KEY>'
        },
        'payload': None
    },
    'data': {
        'Buckets': {
            '<BUCKET NAME>' : {
                <BUCKET FIELDS ...>
            },
            '<BUCKET NAME>' : {
                <BUCKET FIELDS ...>
            },...
        }
    }
}
           
"""

if response['ok']:
    print(len(response['data']['Buckets']))
else:
    print(response['code'], response['reason'])
