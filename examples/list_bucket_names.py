"""
A simple example using the Python SDK to list bucket names from the Igneous system.

This example program assumes that IGNEOUS_API_SERVER and IGNEOUS_API_KEY are set in the environment.
"""
import os
import igneous

client = igneous.Client(api_server=os.environ['IGNEOUS_API_SERVER'], api_key=os.environ['IGNEOUS_API_KEY'])
response: dict = client.buckets_list(names_only=True)

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
        'Buckets': [ <LIST OF BUCKET NAMES> ]
    }
}
           
"""

if response['ok']:
    print(response['data']['Buckets'])
else:
    print(response['code'], response['reason'])
