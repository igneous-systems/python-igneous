"""
A simple example using the Python SDK to retrieve a bucket by name from the Igneous system.

This example program assumes that IGNEOUS_API_SERVER and IGNEOUS_API_KEY are set in the environment.

This example program takes 1 command-line argument:
- the bucket name to retrieve

"""
import os
import sys

import igneous

if len(sys.argv) != 2:
    print("USAGE: ", sys.argv[0], " <bucket name>")
    sys.exit(1)

igneous_bucket_name = sys.argv[1]

client = igneous.Client(api_server=os.environ['IGNEOUS_API_SERVER'], api_key=os.environ['IGNEOUS_API_KEY'])
response: dict = client.buckets_list(match=igneous_bucket_name)

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
            '<BUCKET NAME>': {
            <BUCKET FIELDS>
            }
        }
    }
}
           
"""

print(igneous.pretty_format(response))

"""Example of a successful response:

{
    "code": 200,
    "data": {
        "Buckets": {
            "backup-export-34718": {
                "BackupPolicy": "Bronze",
                "LastCompleted": "2020-10-03T07:06:25.603009Z",
                "LastSize": 10583450,
                "Primary": false,
                "SourcePath": "/smallvol/guirava/src",
                "System": "smallvol.iggy.bz"
            }
        }
    },
    "ok": true,
    "reason": "OK",
    "request": {
        "headers": {
            "Authorization": "WMMKOAO2BWXDHJXTSUHT"
        },
        "method": "get",
        "payload": null,
        "url": "http://10.105.0.22/x/igneous/v1/buckets/"
    }
}
"""